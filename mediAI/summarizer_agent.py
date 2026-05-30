from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from config import GROQ_API_KEY

_llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0
)

SUMMARIZER_SYSTEM_PROMPT = """
You are a Clinical Summarizer Agent inside a hospital information system.

Your only job is to produce a concise, structured medical summary
for the treating doctor.

You may also receive retrieved report context from uploaded PDFs.

OUTPUT FORMAT:

---
**Patient:** <name>
**Email:** <email>

**Appointment History:**
<bullet list>

**Medical & Allergy History:**
<bullet list or None on file>

**Uploaded Report Findings:**
<important findings from reports or None>

**Clinical Notes:**
<2-3 sentence synthesis>
---

STRICT RULES:
- Do NOT fabricate diagnoses.
- Use uploaded reports when available.
- Never hallucinate medications.
- If no data exists write "None on file".
- Keep summary under 300 words.
"""


def run_summarizer(patient_data: dict, rag_context: str = "") -> str:
    """
    Generate doctor-facing patient summary.
    """

    appt_lines = "\n".join(
        f"- {a['doctor']} at {a['time']}"
        for a in patient_data.get("appointments", [])
    )

    if not appt_lines:
        appt_lines = "- None recorded"

    user_content = f"""
PATIENT DATA

Name:
{patient_data.get("patient_name", "Unknown")}

Email:
{patient_data.get("email", "Unknown")}

Medical History:
{patient_data.get("medical_history", "None on file")}

Appointments:
{appt_lines}

Retrieved Medical Reports:
{rag_context}
"""

    try:
        messages = [
            SystemMessage(content=SUMMARIZER_SYSTEM_PROMPT),
            HumanMessage(content=user_content)
        ]

        response = _llm.invoke(messages)

        return response.content

    except Exception as e:
        return f"Summarizer error: {str(e)}"