from typing import Dict, TypedDict, Annotated, List
from langchain_core.documents import Document
from langgraph.graph import add_messages

# State 정의
class GraphState(TypedDict):
    """
    그래프의 상태를 나타내는 데이터 모델
    
    Attributes:
        query (str): 문서 검색 쿼리
        context (List[str]): 문서 검색 결과
        score (str): 문서 판별 점수
        messages (list): 메시지(누적되는 list)
    """
    query: Annotated[str, "문서 검색 쿼리"] 
    docs:Annotated[str, "문서 검색 결과"]
    eval_doc: Annotated[str, "현재 문서 판별 결과"]
    eval_docs: Annotated[List[Dict], "문서 판별 결과"]
    context: Annotated[str, "최종 답변 참고 내용"]
    input: Annotated[str, "입력"]
    refined_input: Annotated[str, "정제된 입력"]
    output: Annotated[str, "출력"]
    tool_calls: Annotated[List[Dict], "도구 호출"]
    messages: Annotated[list, add_messages] 
    

    