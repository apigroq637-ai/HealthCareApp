from database import SessionLocal
from models import PatientProfile


def upsert_patient_permanent_record(email: str, new_notes: str):
    """Saves or appends info to the database."""
    db = SessionLocal()
    patient = db.query(PatientProfile).filter(PatientProfile.email == email).first()

    if patient:
        patient.medical_history = f"{patient.medical_history} | {new_notes}"
    else:
        patient = PatientProfile(email=email, medical_history=new_notes)
        db.add(patient)

    db.commit()
    db.close()
    return "Permanent medical record updated."


def get_patient_permanent_record(email: str):
    """Retrieves info from the database."""
    db = SessionLocal()
    patient = db.query(PatientProfile).filter(PatientProfile.email == email).first()
    db.close()

    if patient:
        return patient.medical_history
    return "No prior medical history found for this email."