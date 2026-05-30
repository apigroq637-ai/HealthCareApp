"""
auth.py — Authentication & Sequential ID Generation
----------------------------------------------------
KEY FIX: When a doctor signs up, we now write to BOTH tables:
  - doctor_users  (auth credentials)
  - doctors       (the table fetch_doctor_schedule tool queries)

This means real-time doctor registration instantly makes them
bookable by patients — no seed file needed.
"""

import hashlib
from database import SessionLocal, Base, engine
from sqlalchemy import Column, Integer, String
from models import Doctor  # ← existing Doctor model used by the agent tool


# ─────────────────────────────────────────────
# AUTH MODELS
# ─────────────────────────────────────────────

class PatientUser(Base):
    __tablename__ = "patient_users"

    id            = Column(Integer, primary_key=True, index=True)
    patient_id    = Column(String, unique=True, index=True)   # e.g. "PT_1"
    name          = Column(String, nullable=False)
    email         = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)


class DoctorUser(Base):
    __tablename__ = "doctor_users"

    id             = Column(Integer, primary_key=True, index=True)
    doctor_id      = Column(String, unique=True, index=True)  # e.g. "Doc_1"
    name           = Column(String, nullable=False)
    email          = Column(String, unique=True, index=True)
    specialization = Column(String, nullable=False)
    available_time = Column(String, nullable=False)
    password_hash  = Column(String, nullable=False)


def init_auth_tables():
    """Create auth tables if they don't exist yet. Call once at app startup."""
    Base.metadata.create_all(bind=engine)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _next_patient_id(db) -> str:
    count = db.query(PatientUser).count()
    next_num = count + 1
    if next_num > 1000:
        raise ValueError("Patient ID limit reached (PT_1000).")
    return f"PT_{next_num}"


def _next_doctor_id(db) -> str:
    count = db.query(DoctorUser).count()
    next_num = count + 1
    if next_num > 100:
        raise ValueError("Doctor ID limit reached (Doc_100).")
    return f"Doc_{next_num}"


# ─────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────

def sign_up(name: str, email: str, password: str, role: str,
            specialization: str = "", available_time: str = "") -> dict:
    """
    Register a new user.

    Patient : name, email, password
    Doctor  : name, email, password, specialization, available_time

    For doctors, also inserts into the `doctors` table so the
    Receptionist agent can find and book them immediately.
    """
    db = SessionLocal()
    try:
        pw_hash = _hash(password)

        # ── PATIENT ──────────────────────────────────────────────────────
        if role == "patient":
            if db.query(PatientUser).filter(PatientUser.email == email).first():
                return {"success": False, "error": "Email already registered as patient."}

            pid = _next_patient_id(db)
            db.add(PatientUser(patient_id=pid, name=name,
                               email=email, password_hash=pw_hash))
            db.commit()
            return {"success": True, "id": pid, "role": "patient", "name": name}

        # ── DOCTOR ───────────────────────────────────────────────────────
        elif role == "doctor":
            if not specialization or not available_time:
                return {"success": False,
                        "error": "Specialization and availability are required for doctors."}
            if db.query(DoctorUser).filter(DoctorUser.email == email).first():
                return {"success": False, "error": "Email already registered as doctor."}

            did = _next_doctor_id(db)

            # 1. Write credentials to doctor_users (auth)
            db.add(DoctorUser(
                doctor_id=did, name=name, email=email,
                specialization=specialization, available_time=available_time,
                password_hash=pw_hash
            ))

            # 2. Write to doctors table so fetch_doctor_schedule tool finds them
            #    Only add if not already present (guard for edge cases)
            existing = db.query(Doctor).filter(Doctor.name.ilike(name)).first()
            if not existing:
                db.add(Doctor(
                    name=name,
                    specialization=specialization,
                    available_time=available_time
                ))

            db.commit()
            return {"success": True, "id": did, "role": "doctor", "name": name}

        else:
            return {"success": False, "error": "Invalid role."}

    except ValueError as ve:
        return {"success": False, "error": str(ve)}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": f"Database error: {str(e)}"}
    finally:
        db.close()


def log_in(user_id: str, password: str, role: str) -> dict:
    """
    Authenticate using Patient ID (PT_3) or Doctor ID (Doc_2).

    Returns:
        {"success": True, "id": "PT_3", "role": "patient", "name": "...", "email": "..."}
        {"success": False, "error": "..."}
    """
    db = SessionLocal()
    try:
        pw_hash = _hash(password)

        if role == "patient":
            user = db.query(PatientUser).filter(
                PatientUser.patient_id == user_id.strip(),
                PatientUser.password_hash == pw_hash
            ).first()
            if not user:
                return {"success": False, "error": "Invalid Patient ID or password."}
            return {"success": True, "id": user.patient_id,
                    "role": "patient", "name": user.name, "email": user.email}

        elif role == "doctor":
            user = db.query(DoctorUser).filter(
                DoctorUser.doctor_id == user_id.strip(),
                DoctorUser.password_hash == pw_hash
            ).first()
            if not user:
                return {"success": False, "error": "Invalid Doctor ID or password."}
            return {"success": True, "id": user.doctor_id,
                    "role": "doctor", "name": user.name, "email": user.email}

        else:
            return {"success": False, "error": "Invalid role."}

    finally:
        db.close()
