from typing import TypedDict, Annotated, List
from langchain_core.documents import Document
from langgraph.graph.message import add_messages

# State 정의
class GraphState(TypedDict):
    """
    그래프의 상태를 나타내는 데이터 모델
    
    Attributes:
        input (str): 사용자 입력
        response (str): 챗봇 응답
        query (str): 문서 검색 쿼리
        context (List[Document]): 문서 검색 결과
        score (str): 문서 판별 점수
        messages (list): 대화 내용
    """
    input: Annotated[str, "사용자 입력"]
    response: Annotated[str, "챗봇 응답"]
    query: Annotated[str, "문서 검색 쿼리"] 
    context: Annotated[List[Document], "문서 검색 결과"]
    score: Annotated[str, "문서 판별 점수"] 
    messages: Annotated[list, add_messages,"대화내용"] 
    

    