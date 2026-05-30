from pydantic import BaseModel

class AppointmentRequest(BaseModel):
    patient_name: str
    doctor_name: str
    appointment_time: str
    email: str