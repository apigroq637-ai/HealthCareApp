from database import Base
from sqlalchemy import Column, Integer, String, Text

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String)
    doctor_name = Column(String)
    appointment_time = Column(String)
    email = Column(String)
    priority = Column(String, default="NORMAL")

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    specialization = Column(String)
    available_time = Column(String)

class PatientProfile(Base):
    __tablename__ = "patient_profiles"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    medical_history = Column(Text)  # This stores the permanent information