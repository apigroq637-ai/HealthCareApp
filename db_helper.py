"""
db_helper.py — Dashboard Data Access Layer
-------------------------------------------
Thin read-only helpers that pull data the dashboards need.
All writes still go through the existing tools (appointment_tool, memory_tool, etc.)

Data flow:
  Doctor Dashboard  → get_all_appointments() → list of dicts
  Doctor Dashboard  → get_patient_summary_data(email) → dict passed to summarizer_agent
  Patient Dashboard → get_patient_appointments(email)  → list of dicts
"""

from database import SessionLocal
from models import Appointment, PatientProfile


# ─────────────────────────────────────────────
# DOCTOR DASHBOARD QUERIES
# ─────────────────────────────────────────────

def get_all_appointments(doctor_name: str) -> list[dict]:
    """
    Returns appointments ONLY for the logged-in doctor.
    """

    db = SessionLocal()

    try:

        rows = db.query(Appointment).filter(
            Appointment.doctor_name.ilike(f"%{doctor_name}%")
        ).order_by(Appointment.id.desc()).all()

        return [
            {
                "id": appt.id,
                "patient_name": appt.patient_name,
                "doctor_name": appt.doctor_name,
                "appointment_time": appt.appointment_time,
                "email": appt.email,
                "priority": appt.priority or "NORMAL"
            }
            for appt in rows
        ]

    finally:
        db.close()


def get_patient_summary_data(email: str) -> dict:
    """
    Aggregates all available data for a patient by email.
    This dict is passed directly into the Clinical Summarizer Agent.

    Designed so a future RAG context can be injected alongside it
    without changing this function's callers.
    """
    db = SessionLocal()
    try:
        # Pull appointments for this patient
        appointments = db.query(Appointment).filter(
            Appointment.email == email
        ).all()

        appt_list = [
            {
                "doctor":  a.doctor_name,
                "time":    a.appointment_time,
            }
            for a in appointments
        ]

        # Pull permanent medical history
        profile = db.query(PatientProfile).filter(
            PatientProfile.email == email
        ).first()

        medical_history = profile.medical_history if profile else "No recorded history."

        # Derive patient name from most recent appointment (best effort)
        patient_name = appointments[-1].patient_name if appointments else "Unknown"

        return {
            "patient_name":    patient_name,
            "email":           email,
            "medical_history": medical_history,
            "appointments":    appt_list,
        }
    finally:
        db.close()


# ─────────────────────────────────────────────
# PATIENT DASHBOARD QUERIES
# ─────────────────────────────────────────────

def get_patient_appointments(email: str) -> list[dict]:
    """
    Returns appointments for a specific patient.
    Used by Patient Dashboard to show appointment status.
    """
    db = SessionLocal()
    try:
        rows = db.query(Appointment).filter(
            Appointment.email == email
        ).order_by(Appointment.id.desc()).all()

        return [
            {
                "doctor":  appt.doctor_name,
                "time":    appt.appointment_time,
                "status":  "Scheduled",          # extend with a status column later
            }
            for appt in rows
        ]
    finally:
        db.close()