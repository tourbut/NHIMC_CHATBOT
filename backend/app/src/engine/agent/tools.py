from typing import Dict
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.prompts import PromptTemplate

async def create_mcp_tools(servers:Dict={}):
    """
    Create a MultiServerMCPClient instance and initialize it.
    
    Args:
        servers (Dict): A dictionary containing server configurations.
        Each key is a server name and the value is a dictionary with server details.
    """
    
    client = MultiServerMCPClient(servers)
    
    # Initialize the client
    await client.__aenter__()
    
    tools = client.get_tools()
    
    return tools

def get_retriever_tool(retriever,name: str,description: str,document_prompt:str|None,document_separator="<**\n---\n**>"):
    """
    Create a retriever tool with the given name, description, and document prompt.
    
    Args:
        retriever (BaseRetriever): The retriever instance to use.
        name (str): The name of the tool.
        description (str): A description of the tool.
        document_prompt (str): The prompt template for formatting documents.
    """
    
    retriever_tool = create_retriever_tool(
        retriever,
        name,
        description,
        document_prompt=PromptTemplate.from_template(document_prompt) if document_prompt else None,
        document_separator=document_separator
    )
    
    return retriever_tool