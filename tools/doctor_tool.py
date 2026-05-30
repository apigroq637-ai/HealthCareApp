from langchain.tools import tool
from database import SessionLocal
from models import Doctor

@tool
def fetch_doctor_schedule(doctor_name: str):
    """
    Queries the database to find a doctor's specialization and available time slots.
    Use this when a user asks about a doctor's availability or specialty.
    """
    db = SessionLocal()
    doctor = db.query(Doctor).filter(
        Doctor.name.ilike(f"%{doctor_name}%")
    ).first()
    db.close()

    if not doctor:
        return "Doctor not found"

    return f"{doctor.name} ({doctor.specialization}) available at {doctor.available_time}"