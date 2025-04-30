from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage,ToolMessage,AIMessage
from langchain_core.output_parsers import PydanticOutputParser

from app.src.utils.graph import draw_graph
from .state import GraphState
from ..common.output import Score
from ..common.prompt import (
    rerank_prompt,
    agent_rag_prompt,
    refine_input_prompt,
    final_generate_prompt,
)
import json
from langchain_core.messages import ToolMessage

class BasicToolNode:
    """Run tools requested in the last AIMessage node"""

    def __init__(self, tools: list) -> None:
        # 도구 리스트
        self.tools_list = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        # 메시지가 존재할 경우 가장 최근 메시지 1개 추출
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")

        # 도구 호출 결과
        outputs = []
        for tool_call in message.tool_calls:
            # 도구 호출 후 결과 저장
            tool_result = self.tools_list[tool_call["name"]].invoke(tool_call["args"])
            outputs.append(
                # 도구 호출 결과를 메시지로 저장
                ToolMessage(
                    content=json.dumps(
                        tool_result, ensure_ascii=False
                    ),  # 도구 호출 결과를 문자열로 변환
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )

        return {"messages": outputs}
            

def create_agent_rag(llm,json_llm,tools,checkpointer,document_options={}):
    """
    Create a RAG agent with a state graph.
    The agent will use the provided LLM and tools to perform its tasks.
    The graph will be compiled and returned.
    
    Args:
        llm: The LLM to be used by the agent.
        json_llm: The LLM for JSON processing.
        tools: The tools to be used by the agent.
        checkpointer: The checkpointer for the graph.
        document_options: Options for document processing.
    
    Graph Structure:
                        +-----------+
                        | __start__ |
                        +-----------+
                            *
                            *
                            *
                        +-------+
                        | agent |.
                    ...+-------+ ....
                    ...        *        ....
                ....           *            ...
            ..               *               ....
    +----------+               *                   ..
    | retrieve |               *                    .
    +----------+....           *                    .
        .         ...        *                    .
        .            ....    *                    .
        .                ..  *                    .
    +----------+          +---------+              ..
    | generate |          | rewrite |          ....
    +----------+****      +---------+       ...
                    ***                 ....
                    ****         ....
                        **     ..
                        +---------+
                        | __end__ |
                        +---------+
    """

    def agent(state:GraphState) -> GraphState:
        
        input = state.get('input')
        refined_input = state.get('refined_input')
        
        prompt = agent_rag_prompt(document_options.get("document_metadata", "부서별 업무분장"))

        # retriever tool 바인딩
        chain = prompt|llm.bind_tools(tools)

        # 에이전트 응답 생성
        response = chain.invoke({"input": input if not refined_input else refined_input})

        if len(response.tool_calls) > 0:
            state['tool_calls'] = response.tool_calls
        else :
            state['output'] = response.content
        
        state['messages'] = [HumanMessage(content=input),response]
        
        return state

    def rerank(state:GraphState) -> GraphState:
        
        # 질문 추출
        input = state.get('input')
        refined_input = state.get('refined_input') # 질문 재작성된 경우

        # 현재 상태에서 메시지 추출
        # Tool 메시지 추출 
        messages = state.get("messages")
        
        # ToolMessage에서 검색 결과 추출
        tool_message = None
        for msg in reversed(messages):
            if isinstance(msg, ToolMessage):
                tool_message = msg.content
                break
        
        # 문서 분리
        document_separator = document_options.get("document_separator", "<**\n---\n**>")
        retrieved_docs = tool_message.split(document_separator)
        
        # 관련성 평가 프롬프트 구성
        prompt = rerank_prompt()
        chain = prompt|json_llm.with_structured_output(Score)
        
        # 관련성 평가 실행
        scored_result=[]
        for doc in retrieved_docs:
            score = chain.invoke({"input": input if not refined_input else refined_input, "context": doc})
            scored_result.append({"score":score,
                                  "total_score":score.relevant_score + score.keyward_matching_score + score.specific_score + score.irrelevant_score + score.logical_error_score,
                                  "doc":doc})

        # 관련성 여부 추출
        # 7점 이상인 경우 인덱스 추출
        filtered_docs = []
        
        for result in scored_result:
            if result.get('score') is None:
                continue
            if result.get('total_score') >= 7:
                filtered_docs.append(result)
        
        # 점수 기준으로 정렬
        if len(filtered_docs) > 0:
            filtered_docs = sorted(filtered_docs, key=lambda x: x.get('total_score'), reverse=True)
        
        # 문서 적합성 점수 계산
        context = []
        for result in filtered_docs:
            doc = f"**검색 문서 적합 점수**: {result.get('total_score')} \n"
            doc += f"```검색결과\n{result.get('doc')}```\n\n\n"
            context.append(doc)
        
        state['context'] = context
        return state

    def router_rerank(state:GraphState) -> Literal["generate", "rewrite"]:
        """
        Determine the next action based on the state of the workflow.
        If the state contains a context, proceed to the 'generate' node.
        Otherwise, proceed to the 'rewrite' node.
        """
        if len(state.get('context')) > 0:
            return "generate"
        else:
            return "rewrite"
        
    def rewrite(state:GraphState) -> GraphState:
        # 현재 상태에서 메시지 추출
        # 원래 질문 추출
        question = state["input"]

        # 질문 개선을 위한 프롬프트 구성
        prompt = refine_input_prompt(document_options.get("document_metadata", "부서별 업무분장"))

        # LLM 모델로 질문 개선
        # Query-Transform 체인 실행
        chain = prompt|llm
        response = chain.invoke({"input": question})
        state['refined_input'] = response.content
        
        # 재작성된 질문 반환
        state["messages"] = [response]
        
        return state

    def generate(state:GraphState) -> GraphState:
        # 현재 상태에서 메시지 추출
        messages = state.get("messages")

        # 원래 질문 추출
        input = state.get("input")

        # 가장 마지막 메시지 추출
        context = "\n".join(state["context"])

        # RAG 프롬프트 템플릿 가져오기
        prompt = final_generate_prompt()

        # LLM 모델 초기화

        # RAG 체인 구성
        rag_chain = prompt | llm

        # 답변 생성 실행
        response = rag_chain.invoke({"context": context, "input": input})
        
        state["output"] = response.content
        state["messages"] = [response]
        return state
    
    
    ## 노드 생성
    workflow = StateGraph(GraphState)
    workflow.add_node("agent", agent)  # 에이전트 노드
    workflow.add_node("rerank", rerank)  # 문서 품질 평가 노드
    retrieve = ToolNode(tools)
    workflow.add_node("retrieve", retrieve)  # 검색 노드
    workflow.add_node("rewrite", rewrite)  # 질문 재작성 노드
    workflow.add_node("generate", generate)  # 관련 문서 확인 후 응답 생성 노드
    
    # Node에 Edge 추가
    
    # 시작점에서 에이전트 노드로 연결(START > agent)
    workflow.add_edge(START, "agent") 

    # 검색 여부 결정을 위한 조건부 엣지 추가
    # 도구가 존재하는 경우 (agent > retrieve)
    # 도구가 없으면 (agent > END)
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "retrieve",
            END: END,
        },
    )
    
    # 검색 노드에서 문서 품질 평가 노드로 연결(retrieve > rerank)
    workflow.add_edge("retrieve", "rerank")

    # 문서 품질 평가 노드에서 context가 존재하는 경우(rerank > generate)
    # context가 존재하지 않는 경우(rerank > rewrite)
    workflow.add_conditional_edges(
        "rerank",
        # 문서 품질 평가
        router_rerank,
    )
    
    # 질문 재작성 노드에서 Agent 노드로 연결(rewrite > agent)
    workflow.add_edge("rewrite", "agent")
    
    # 최종 답변 생성 노드로 연결(generate > END)
    workflow.add_edge("generate", END)

    # 워크플로우 그래프 컴파일
    graph = workflow.compile(checkpointer=checkpointer)
    
    return graph

def acreate_agent_rag(llm,json_llm,tools,checkpointer,document_options={}):
    """
    Create a RAG agent with a state graph.
    The agent will use the provided LLM and tools to perform its tasks.
    The graph will be compiled and returned.
    
    Args:
        llm: The LLM to be used by the agent.
        json_llm: The LLM for JSON processing.
        tools: The tools to be used by the agent.
        checkpointer: The checkpointer for the graph.
        document_options: Options for document processing.
    
    Graph Structure:
                    +-----------+
                    | __start__ |
                    +-----------+
                          *
                          *
                          *
                      +-------+
                      | agent |.
                  ....+-------+ ...
               ...        *        ....
           ....           *            ...
         ..               *               ...
+----------+              *                  ..
| retrieve |              *                   .
+----------+              *                   .
      *                   *                   .
      *                   *                   .
      *                   *                   .
 +--------+               *                   .
 | rerank |               *                   .
 +--------+....           *                   .
      .        ...        *                   .
      .           ....    *                   .
      .               ..  *                   .
+----------+         +---------+             ..
| generate |         | rewrite |          ...
+----------+***      +---------+       ...
               ***                 ....
                  ****          ...
                      **      ..
                     +---------+
                     | __end__ |
                     +---------+
    """

    async def agent(state:GraphState) -> GraphState:
        
        input = state.get('input')
        refined_input = state.get('refined_input')
        
        prompt = agent_rag_prompt(document_options.get("document_metadata", "부서별 업무분장"))

        # retriever tool 바인딩
        chain = prompt|llm.bind_tools(tools)

        # 에이전트 응답 생성
        response = await chain.ainvoke({"input": input if not refined_input else refined_input})

        if len(response.tool_calls) > 0:
            state['tool_calls'] = response.tool_calls
        else :
            state['output'] = response.content
        
        state['messages'] = [HumanMessage(content=input),response]
        
        return state
    
    async def rerank(state:GraphState) -> GraphState:
        
        # 질문 추출
        input = state.get('input')
        refined_input = state.get('refined_input') # 질문 재작성된 경우

        # 현재 상태에서 메시지 추출
        # Tool 메시지 추출 
        messages = state.get("messages")
        
        # ToolMessage에서 검색 결과 추출
        tool_message = None
        for msg in reversed(messages):
            if isinstance(msg, ToolMessage):
                tool_message = msg.content
                break
        
        # 문서 분리
        document_separator = document_options.get("document_separator", "<---split--->")
        retrieved_docs = tool_message.split(document_separator)
        state['docs'] = retrieved_docs
        
        
        # 관련성 평가 프롬프트 구성
        parser = PydanticOutputParser(pydantic_object=Score)
        prompt = rerank_prompt(parser)
        chain = prompt|json_llm|parser
        
        # 관련성 평가 실행
        scored_result=[]
        for doc in retrieved_docs:
            score = await chain.ainvoke({"input": input if not refined_input else refined_input, "context": doc})
            total_score = score.relevant_score + score.keyward_matching_score + score.specific_score + score.irrelevant_score + score.logical_error_score
            refine_doc = f"**검색 문서 적합 점수**: {total_score} \n"
            refine_doc += f"```검색결과\n{doc}```\n\n\n"
            scored_result.append({"score":score,
                                  "total_score":total_score,
                                  "doc":refine_doc})
            state['context'] = refine_doc
            yield state

        # 관련성 여부 추출
        # 7점 이상인 경우 인덱스 추출
        filtered_docs = []
        
        for result in scored_result:
            if result.get('score') is None:
                continue
            if result.get('total_score') >= 7:
                filtered_docs.append(result)
        
        # 점수 기준으로 정렬
        if len(filtered_docs) > 0:
            filtered_docs = sorted(filtered_docs, key=lambda x: x.get('total_score'), reverse=True)
        
        # 문서 적합성 점수 계산
        context = []
        for result in filtered_docs:
            context.append(result.get('doc'))
        
        state['context'] = context
        yield state

    async def router_rerank(state:GraphState) -> Literal["generate", "rewrite"]:
        """
        Determine the next action based on the state of the workflow.
        If the state contains a context, proceed to the 'generate' node.
        Otherwise, proceed to the 'rewrite' node.
        """
        if len(state.get('context')) > 0:
            return "generate"
        else:
            return "rewrite"
        
    async def rewrite(state:GraphState) -> GraphState:
        # 현재 상태에서 메시지 추출
        # 원래 질문 추출
        question = state["input"]

        # 질문 개선을 위한 프롬프트 구성
        prompt = refine_input_prompt(document_options.get("document_metadata", "부서별 업무분장"))

        # LLM 모델로 질문 개선
        # Query-Transform 체인 실행
        chain = prompt|llm
        response = await chain.ainvoke({"input": question})
        state['refined_input'] = response.content
        
        # 재작성된 질문 반환
        state["messages"] = [response]
        
        return state

    async def generate(state:GraphState) -> GraphState:
        # 현재 상태에서 메시지 추출
        messages = state.get("messages")

        # 원래 질문 추출
        input = state.get("input")

        # 가장 마지막 메시지 추출
        context = "\n".join(state["context"])

        # RAG 프롬프트 템플릿 가져오기
        prompt = final_generate_prompt()

        # LLM 모델 초기화

        # RAG 체인 구성
        rag_chain = prompt | llm

        # 답변 생성 실행
        response = await rag_chain.ainvoke({"context": context, "input": input})
        
        state["output"] = response.content
        state["messages"] = [response]
        return state
    
    
    workflow = StateGraph(GraphState)
    
    ## 노드 생성
    workflow.add_node("agent", agent)  # 에이전트 노드
    workflow.add_node("rerank", rerank)  # 문서 품질 평가 노드
    retrieve = BasicToolNode(tools)
    workflow.add_node("retrieve", retrieve)  # 검색 노드
    workflow.add_node("rewrite", rewrite)  # 질문 재작성 노드
    workflow.add_node("generate", generate)  # 관련 문서 확인 후 응답 생성 노드
    
    # Node에 Edge 추가
    
    # 시작점에서 에이전트 노드로 연결(START > agent)
    workflow.add_edge(START, "agent") 

    # 검색 여부 결정을 위한 조건부 엣지 추가
    # 도구가 존재하는 경우 (agent > retrieve)
    # 도구가 없으면 (agent > END)
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "retrieve",
            END: END,
        },
    )
    
    # 검색 노드에서 문서 품질 평가 노드로 연결(retrieve > rerank)
    workflow.add_edge("retrieve", "rerank")

    # 문서 품질 평가 노드에서 context가 존재하는 경우(rerank > generate)
    # context가 존재하지 않는 경우(rerank > rewrite)
    workflow.add_conditional_edges(
        "rerank",
        # 문서 품질 평가
        router_rerank,
    )
    
    # 질문 재작성 노드에서 Agent 노드로 연결(rewrite > agent)
    workflow.add_edge("rewrite", "agent")
    
    # 최종 답변 생성 노드로 연결(generate > END)
    workflow.add_edge("generate", END)

    # 워크플로우 그래프 컴파일
    graph = workflow.compile(checkpointer=checkpointer)
    
    return graph

def acreate_agent_rag_v2(llm,json_llm,tools,checkpointer,document_options={}):
    """
    Create a RAG agent with a state graph.
    The agent will use the provided LLM and tools to perform its tasks.
    The graph will be compiled and returned.
    
    Args:
        llm: The LLM to be used by the agent.
        json_llm: The LLM for JSON processing.
        tools: The tools to be used by the agent.
        checkpointer: The checkpointer for the graph.
        document_options: Options for document processing.
    
    Graph Structure:
                    +-----------+
                    | __start__ |
                    +-----------+
                          *
                          *
                          *
                      +-------+
                      | agent |.
                  ....+-------+ ...
               ...        *        ....
           ....           *            ...
         ..               *               ...
+----------+              *                  ..
| retrieve |              *                   .
+----------+              *                   .
      *                   *                   .
      *                   *                   .
      *                   *                   .
 +--------+               *                   .
 | rerank |               *                   .
 +--------+....           *                   .
      .        ...        *                   .
      .           ....    *                   .
      .               ..  *                   .
+----------+         +---------+             ..
| generate |         | rewrite |          ...
+----------+***      +---------+       ...
               ***                 ....
                  ****          ...
                      **      ..
                     +---------+
                     | __end__ |
                     +---------+
    """

    async def agent(state:GraphState) -> GraphState:
        
        input = state.get('input')
        refined_input = state.get('refined_input')
        
        prompt = agent_rag_prompt(document_options.get("document_metadata", "부서별 업무분장"))

        # retriever tool 바인딩
        chain = prompt|llm.bind_tools(tools)

        # 에이전트 응답 생성
        response = await chain.ainvoke({"input": input if not refined_input else refined_input})

        if len(response.tool_calls) > 0:
            state['tool_calls'] = response.tool_calls
        else :
            state['output'] = response.content
        
        state['messages'] = [HumanMessage(content=input),response]
        
        return state
    
    async def split_docs(state:GraphState) -> GraphState:
        # 현재 상태에서 메시지 추출
        # Tool 메시지 추출 
        messages = state.get("messages")
        
        # ToolMessage에서 검색 결과 추출
        tool_message = None
        for msg in reversed(messages):
            if isinstance(msg, ToolMessage):
                tool_message = msg.content
                tool_message = tool_message.replace("\\n", "\n")
                break
        
        # 문서 분리
        document_separator = document_options.get("document_separator", "<---split--->")
        retrieved_docs = tool_message.split(document_separator)
        state['docs'] = retrieved_docs
        
        return state    
    
    async def rerank(state:GraphState) -> GraphState:
        
        # 질문 추출
        input = state.get('input')
        refined_input = state.get('refined_input') # 질문 재작성된 경우
        eval_docs = state.get('eval_docs',[]) 
        if len(state.get('docs')) == 0:
            return state
        
        doc = state.get('docs').pop(0)

        
        # 관련성 평가 프롬프트 구성
        parser = PydanticOutputParser(pydantic_object=Score)
        prompt = rerank_prompt(parser)
        chain = prompt|json_llm|parser
        
        # 관련성 평가 실행

        score = await chain.ainvoke({"input": input if not refined_input else refined_input, "context": doc})
        total_score = score.relevant_score + score.keyward_matching_score + score.specific_score + score.irrelevant_score + score.logical_error_score
        eval_doc = f"""**검색 문서 적합 점수**: {total_score} \n"""
        eval_doc += f"""```검색결과\n{doc}\n```\n\n"""
        state['eval_doc'] = eval_doc
        
        if total_score >= 7:
            if len(eval_docs) > 0:
                eval_docs.append({"doc":eval_doc,"total_score":total_score})
            else:
                eval_docs = [{"doc":eval_doc,"total_score":total_score}]
                
        state['eval_docs'] = eval_docs
        
        return state

    async def router_rerank(state:GraphState) -> Literal["rerank","generate", "rewrite"]:
        """
        Determine the next action based on the state of the workflow.
        If the state contains a context, proceed to the 'generate' node.
        Otherwise, proceed to the 'rewrite' node.
        """
        if len(state.get('docs')) > 0:
            return "rerank"
        else :
            if len(state.get('eval_docs')) > 0:
                return "generate"
            else:
                return "rewrite"
        
    async def rewrite(state:GraphState) -> GraphState:
        # 현재 상태에서 메시지 추출
        # 원래 질문 추출
        question = state["input"]

        # 질문 개선을 위한 프롬프트 구성
        prompt = refine_input_prompt(document_options.get("document_metadata", "부서별 업무분장"))

        # LLM 모델로 질문 개선
        # Query-Transform 체인 실행
        chain = prompt|llm
        response = await chain.ainvoke({"input": question})
        state['refined_input'] = response.content
        
        # 재작성된 질문 반환
        state["messages"] = [response]
        
        return state

    async def generate(state:GraphState) -> GraphState:
        # 현재 상태에서 메시지 추출
        messages = state.get("messages")

        # 원래 질문 추출
        input = state.get("input")

        eval_docs = state["eval_docs"]
        
        # context = {"doc":doc,"total_score":total_score}
        #total_score 내림차순으로 정렬 후 상위 2개의 doc 출력
        context = sorted(eval_docs, key=lambda x: x.get('total_score'), reverse=True)
        context = context[:2]
        context = [doc.get('doc') for doc in context]
        context = "\n\n".join(context)
        state["context"] = context
        
        # 가장 마지막 메시지 추출

        # RAG 프롬프트 템플릿 가져오기
        prompt = final_generate_prompt()

        # LLM 모델 초기화

        # RAG 체인 구성
        rag_chain = prompt | llm

        # 답변 생성 실행
        response = await rag_chain.ainvoke({"context": context, "input": input})
        
        state["output"] = response.content
        state["messages"] = [response]
        return state
    
    workflow = StateGraph(GraphState)
    
    ## 노드 생성
    workflow.add_node("agent", agent)  # 에이전트 노드
    workflow.add_node("split_docs", split_docs)  # 문서 분리 노드
    workflow.add_node("rerank", rerank)  # 문서 품질 평가 노드
    workflow.add_node("retrieve", BasicToolNode(tools))  # 검색 노드
    workflow.add_node("rewrite", rewrite)  # 질문 재작성 노드
    workflow.add_node("generate", generate)  # 관련 문서 확인 후 응답 생성 노드
    
    # Node에 Edge 추가
    
    # 시작점에서 에이전트 노드로 연결(START > agent)
    workflow.add_edge(START, "agent") 

    # 검색 여부 결정을 위한 조건부 엣지 추가
    # 도구가 존재하는 경우 (agent > retrieve)
    # 도구가 없으면 (agent > END)
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "retrieve",
            END: END,
        },
    )
    
    # 검색 노드에서 문서 품질 평가 노드로 연결(retrieve > rerank)
    workflow.add_edge("retrieve", "split_docs")
    workflow.add_edge("split_docs", "rerank")

    # 문서 품질 평가 노드에서 context가 존재하는 경우(rerank > generate)
    # context가 존재하지 않는 경우(rerank > rewrite)
    workflow.add_conditional_edges(
        "rerank",
        # 문서 품질 평가
        router_rerank,
    )
    
    # 질문 재작성 노드에서 Agent 노드로 연결(rewrite > agent)
    workflow.add_edge("rewrite", "agent")
    
    # 최종 답변 생성 노드로 연결(generate > END)
    workflow.add_edge("generate", END)

    # 워크플로우 그래프 컴파일
    graph = workflow.compile(checkpointer=checkpointer)
    
    #draw_graph(graph)
    
    return graph