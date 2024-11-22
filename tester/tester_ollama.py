from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate,ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import StrOutputParser

from langchain_ollama import ChatOllama
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough,RunnableParallel
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from operator import itemgetter

strparser = StrOutputParser()

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any

class AIThink(BaseModel):
    THOUGHT: str = Field(..., title="모델이 생각하는 내용")
    search_msg: str = Field(..., title="문서에서 검색하려는 내용")
    
pydantic_parser = PydanticOutputParser(pydantic_object=AIThink)

def get_thinking_prompt(pydantic_parser:PydanticOutputParser):
    template="""
<INSTRUCTION>
You're in the process of carefully reviewing a user's question or request.
Your job is to interpret the user's input and generate search terms to retrieve that information from the documentation.
You also review the <CHAT_HISTORY> section to refer to past interactions to understand the user's question.
If the question is poorly worded, prompt further inquiry.
</INSTRUCTION>
<INPUT>
{input}
</INPUT>
{format_instructions}
"""
    return PromptTemplate(
        template=template,
        input_variables=["chat_history", "input"],
        partial_variables={"format_instructions": pydantic_parser.get_format_instructions()}
    )
    
def get_thinking_chatbot():
    return ChatPromptTemplate.from_messages(
    [
        ("system", """
<INSTRUCTION>
You are an intelligent virtual assistant designed to help users.
Your interactions should always be friendly, empathetic, and clear.
When responding to user questions, you provide accurate and useful answers, taking the time to think through each question carefully and respond in a logical and systematic manner.
Always consider the <THOUGHT> section as a reflection of your reasoning process before finalizing your response. Use this to ensure that your answers are well-thought-out and effectively address the user's needs.

When necessary, you can offer additional relevant information.
While you can proactively guide or suggest ideas in the conversation, you must always respect the user's intent.
For complex questions, focus on explaining concepts in a simple and accessible way, avoiding jargon when possible.
Your goal is to maintain a positive and cooperative attitude, building trust with the user throughout the interaction.

As you interact with the user, continuously learn and adapt to their preferences, using previous conversations to offer more personalized and relevant responses in future interactions.

If you make a mistake or if the user seems confused or dissatisfied with your response, acknowledge it, apologize if necessary, and strive to provide the correct or clearer information.

Always adhere to ethical guidelines, especially regarding user privacy and sensitive topics. Never store, share, or misuse any personal or sensitive information provided by the user. Ensure that the user's data is handled with the highest level of confidentiality and respect.

</INSTRUCTION>

<THOUGHT>
{thought}
</THOUGHT>
<CONTEXT>
{context}
</CONTEXT>
"""),
        ("human", "{input}"),
    ]
    )
    


llm = ChatOllama(model="qwen2.5:14b",base_url= "http://192.168.1.73:11434")
think_prompt = get_thinking_prompt(pydantic_parser)
prompt = get_thinking_chatbot()

think_chain = think_prompt|llm|pydantic_parser
answer_chain = prompt|llm

def get_thought(output):
    return output["thought"].THOUGHT

def get_context(output):
    print("log: ",output["thought"].search_msg)
    return ""

def output_formatter(output):
    return {
        "thought": output["thought"],
        "answer": output["answer"]
    }
    
final_chain = (
    RunnableParallel(
        thought = think_chain,
        input = RunnablePassthrough()
    )
    |{
        "thought":RunnableLambda(get_thought),
        "context":RunnableLambda(get_context),
        "input" : RunnablePassthrough()
    }|
    {
        "thought":RunnablePassthrough(),
        "context":RunnablePassthrough(),
        "answer":answer_chain
    }
    |RunnableLambda(output_formatter)
    )

print(final_chain.invoke({'input':'안녕'}))