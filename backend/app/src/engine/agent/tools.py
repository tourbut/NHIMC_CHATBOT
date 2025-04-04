from typing import Dict
from langchain_mcp_adapters.client import MultiServerMCPClient

async def create_mcp_tools(servers:Dict={}):
    
    client = MultiServerMCPClient(servers)
    
    # Initialize the client
    await client.__aenter__()
    
    tools = client.get_tools()
    
    return tools