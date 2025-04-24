from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)

from app.src.deps import engine
from app.src.engine.llms.memory import pg_ParentDocumentRetriever
from app.src.engine.llms.chain import (
    create_llm,
)
from app.src.engine.agent.node_graph import (
    create_agent_rag
)  
from app.src.engine.agent.tools import create_mcp_tools,get_retriever_tool

from app.src.utils.graph import draw_graph

def load_retriever():
    collection_name='a8caad1111f94445bea57d2a1a82ad56'
    retriever = pg_ParentDocumentRetriever(connection=engine,
                                    collection_name=collection_name,
                                    api_key='-',
                                    source='ollama',
                                    model='bge-m3',
                                    base_url='http://192.168.1.24:11434',
                                    async_mode=False,
                                    search_kwargs={"k": 500, "lambda": 0.3},
                                    )
    return retriever

if __name__ == "__main__":
    
    retriever = load_retriever()
    document_options = {"document_prompt": "{page_content}",
                        "document_separator": "<**\n---\n**>",
                        "document_metadata": """ 국민건강보험 일산병원 부서별 업무분장(담당자/업무내용/내선번호)
                        부서현황: 재무관리부,환자경험혁신부,구매관리부,의학독서실,기획예산부,총무부,간호지원부,의무기록부,의료정보기획부,의료정보운영부
                        """
                        }
    retriever_tool = get_retriever_tool(
        retriever=retriever,
        name="retriever",
        description="Search and return information about 부서별 업무분장. it contains the information about 부서별 업무분장.",
        document_prompt=document_options.get("document_prompt"),
        document_separator=document_options.get("document_separator")
    )
    
    llm = create_llm(source='ollama',
                model='mistral-small3.1:latest',
                api_key='-',
                base_url='http://192.168.1.73:11434',
                temperature=0.2,
                )
    
    json_llm = create_llm(source='ollama',
                model='mistral-small3.1:latest',
                api_key='-',
                format="json",
                base_url='http://192.168.1.73:11434',
                temperature=0,
                )
 
    tools = [retriever_tool]
    checkpointer = MemorySaver()
    
    graph = create_agent_rag(llm=llm,
                             json_llm=json_llm,
                             tools=tools,
                             checkpointer=checkpointer,
                             document_options=document_options)

    config = RunnableConfig(
        recursion_limit=10,  # 최대 10개의 노드까지 방문. 그 이상은 RecursionError 발생
        configurable={"thread_id": "test01"},  # 스레드 ID 설정
        stream_mode = "values"
    )
    
    draw_graph(graph)
    
    input ="정보보안 담당자 연락처를 업무분장에서 찾아줘."
    
    final_state = graph.invoke({"input": input}, config=config) 
    
    print(final_state.get('output'))
    
    
