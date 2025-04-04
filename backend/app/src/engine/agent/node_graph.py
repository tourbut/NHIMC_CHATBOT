import re
from typing import TypedDict, Annotated, List
from langchain_core.documents import Document
from langchain_mcp_adapters.client import MultiServerMCPClient

from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from .state import GraphState


def create_chatbot_node(llm,tools):
    
    async def chatbot(state:GraphState) -> GraphState:
        """
        챗봇 노드
        """
        
        input = state["input"]
        state['messages'] = [("user", input)]
        
        # 챗봇 노드 생성
        llm_with_tools = llm.bind_tools(tools)
        
        # 챗봇 노드 실행
        response=llm_with_tools.invoke(state["messages"])
        
        return GraphState(response=response,messages=[("assistant", response)])
    
    return chatbot