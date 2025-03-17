from contextlib import contextmanager
from typing import Generator
from langchain_core.callbacks import BaseCallbackHandler,AsyncCallbackHandler
from langchain_community.callbacks import get_openai_callback
import asyncio

class token_counter_callback(BaseCallbackHandler):
    def __init__(self):
        self.total_tokens = 0
        self.completion_tokens = 0
        
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.completion_tokens += 1
        self.total_tokens += 1
        
    def get_token_count(self):
        return {
            "total_tokens": self.total_tokens,
            "completion_tokens": self.completion_tokens
        }
        
class MyCallback(AsyncCallbackHandler):
    def __init__(self):
        self.token_queue = asyncio.Queue()
        self.done = asyncio.Event()

    async def on_llm_new_token(self, token: str, **kwargs):
        await self.token_queue.put(token)

    async def on_chain_end(self, outputs, **kwargs):
        self.done.set()
        
@contextmanager
def get_my_callback() -> Generator[token_counter_callback, None, None]:
    
    cb = token_counter_callback()
    yield cb
