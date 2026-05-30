from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from config import GROQ_API_KEY

from tools.memory_tool import (
    record_medical_history,
    fetch_medical_history
)

from agents.prompts.memory_prompt import MEMORY_PROMPT

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0
)

tools = [
    record_medical_history,
    fetch_medical_history
]

memory_agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=MEMORY_PROMPT
)