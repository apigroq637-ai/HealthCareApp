from langchain.tools import tool
from memory_store.permanent_memory import upsert_patient_permanent_record, get_patient_permanent_record

@tool
def record_medical_history(email: str, information: str):
    """
    Use this tool to save permanent medical info like allergies or chronic illnesses.
    """
    return upsert_patient_permanent_record(email, information)

@tool
def fetch_medical_history(email: str):
    """
    Use this tool to look up a patient's permanent medical history and allergies.
    """
    return get_patient_permanent_record(email)