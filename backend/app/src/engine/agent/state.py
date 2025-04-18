from typing import TypedDict, Annotated, List
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
    context: Annotated[List[str], "문서 검색 결과"]
    input: Annotated[str, "입력"]
    refined_input: Annotated[str, "정제된 입력"]
    output: Annotated[str, "출력"]
    tool_calls: Annotated[List[dict], "도구 호출"]
    messages: Annotated[list, add_messages] 
    

    