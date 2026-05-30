from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from config import GROQ_API_KEY

from tools.appointment_tool import (
    book_appointment,
    get_available_slots,
    get_current_datetime
)

from tools.doctor_tool import fetch_doctor_schedule
from tools.email_tool import send_email

from agents.prompts.receptionist_prompt import RECEPTIONIST_PROMPT

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0
)

tools = [
    get_current_datetime,
    get_available_slots,
    fetch_doctor_schedule,
    book_appointment,
    send_email
]

receptionist_agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=RECEPTIONIST_PROMPT
)