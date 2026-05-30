from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from config import GROQ_API_KEY

from tools.clinical_triage_tool import clinical_triage
from tools.memory_tool import fetch_medical_history

from agents.prompts.reasoning_prompt import REASONING_PROMPT

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0
)

tools = [
    clinical_triage,
    fetch_medical_history
]

reasoning_agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=REASONING_PROMPT
)