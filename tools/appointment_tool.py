"""
tools/appointment_tool.py — Smart Appointment Booking with Priority Management
---------------------------------------------------------------------------
Changes:
- Critical patients are prioritized.
- If no slot is free for a CRITICAL patient, a normal patient is moved to the next day.
- Rescheduled patients receive updated email notifications.
- Keeps original project structure and minimal logic changes.
"""

from datetime import datetime, timedelta
from langchain.tools import tool
from database import SessionLocal
from models import Appointment, Doctor
from tools.email_tool import send_reschedule_email


# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _parse_time(time_str: str) -> datetime | None:
    """
    Parse a time string into a datetime object.
    """
    formats = ["%I %p", "%I:%M %p", "%H:%M", "%H", "%I%p", "%I:%M%p"]

    time_str = time_str.strip()

    for fmt in formats:
        try:
            t = datetime.strptime(time_str.upper(), fmt)
            now = datetime.now()

            return t.replace(
                year=now.year,
                month=now.month,
                day=now.day
            )

        except ValueError:
            continue

    return None


def _extract_doctor_window(available_time: str):
    """
    Parse doctor working hours.

    Example:
    '9 AM - 5 PM'
    """
    parts = [
        p.strip()
        for p in available_time.replace("–", "-").split("-")
    ]

    if len(parts) < 2:
        return None, None

    return _parse_time(parts[0]), _parse_time(parts[1])


def _get_booked_datetimes(doctor_name: str, date_str: str) -> list:
    """
    Retrieve booked appointments for a doctor on a specific date.
    """
    db = SessionLocal()

    try:
        rows = db.query(Appointment).filter(
            Appointment.doctor_name.ilike(f"%{doctor_name}%")
        ).all()

        booked = []

        for row in rows:

            for fmt in [
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d %I:%M %p",
                "%Y-%m-%d %I %p"
            ]:

                try:
                    dt = datetime.strptime(
                        row.appointment_time.strip(),
                        fmt
                    )

                    if dt.strftime("%Y-%m-%d") == date_str:
                        booked.append(dt)

                    break

                except ValueError:
                    continue

        return booked

    finally:
        db.close()


def _compute_free_slots(
    start: datetime,
    end: datetime,
    booked: list,
    slot_hours: int = 2
) -> list:
    """
    Compute free appointment slots.
    """
    free = []
    current = start

    while current + timedelta(hours=slot_hours) <= end:

        collision = any(
            abs((current - b).total_seconds()) < 1800
            for b in booked
        )

        if not collision:
            free.append(
                current.strftime("%I:%M %p").lstrip("0")
                or "12:00 PM"
            )

        current += timedelta(hours=slot_hours)

    return free


# ─────────────────────────────────────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────────────────────────────────────

@tool
def get_current_datetime() -> str:
    """
    Returns the current real-time date and time.

    Always call this first before checking appointments.
    """
    now = datetime.now()

    return now.strftime(
        "Today is %A, %B %d, %Y. Current time: %I:%M %p"
    )


@tool
def get_available_slots(doctor_name: str, date: str) -> str:
    """
    Returns available appointment slots for a doctor.

    Args:
        doctor_name: Doctor name.
        date: Date in YYYY-MM-DD format.
    """
    db = SessionLocal()

    try:
        doctor = db.query(Doctor).filter(
            Doctor.name.ilike(f"%{doctor_name}%")
        ).first()

    finally:
        db.close()

    if not doctor:
        return f"Doctor '{doctor_name}' not found in the system."

    start, end = _extract_doctor_window(
        doctor.available_time
    )

    if not start or not end:
        return (
            f"Could not parse Dr. {doctor.name}'s availability "
            f"('{doctor.available_time}')."
        )

    booked = _get_booked_datetimes(
        doctor_name,
        date
    )

    free = _compute_free_slots(
        start,
        end,
        booked
    )

    if not free:
        return (
            f"Sorry, Dr. {doctor.name} has no available slots on {date}."
        )

    return (
        f"Dr. {doctor.name} ({doctor.specialization}) — "
        f"available slots on {date}: {', '.join(free)}."
    )


@tool
def book_appointment(
    patient_name: str,
    doctor_name: str,
    appointment_time: str,
    email: str,
    priority: str = "NORMAL"
) -> str:
    """
    Books a medical appointment.

    Features:
    - Prevents double-booking.
    - Validates doctor working hours.
    - Prioritizes CRITICAL patients.
    - Reschedules normal patients if required.

    Args:
        patient_name: Full patient name.
        doctor_name: Doctor name.
        appointment_time: Appointment datetime.
        email: Patient email.
        priority: NORMAL or CRITICAL.
    """

    db = SessionLocal()

    try:
        # ─────────────────────────────────────────
        # FIND DOCTOR
        # ─────────────────────────────────────────

        doctor = db.query(Doctor).filter(
            Doctor.name.ilike(f"%{doctor_name}%")
        ).first()

        if not doctor:
            return f"Doctor '{doctor_name}' not found."

        # ─────────────────────────────────────────
        # PARSE REQUESTED TIME
        # ─────────────────────────────────────────

        requested_dt = None

        for fmt in [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %I:%M %p",
            "%Y-%m-%d %I %p"
        ]:
            try:
                requested_dt = datetime.strptime(
                    appointment_time.strip(),
                    fmt
                )
                break

            except ValueError:
                continue

        if not requested_dt:
            return "Invalid appointment time format."

        # ─────────────────────────────────────────
        # CHECK WORKING HOURS
        # ─────────────────────────────────────────

        start, end = _extract_doctor_window(
            doctor.available_time
        )

        if start and end:

            req_cmp = requested_dt.replace(
                year=start.year,
                month=start.month,
                day=start.day
            )

            if not (start <= req_cmp < end):
                return (
                    f"Requested time is outside "
                    f"Dr. {doctor.name}'s working hours."
                )

        # ─────────────────────────────────────────
        # PREVENT DUPLICATE BOOKINGS
        # Must run BEFORE conflict resolution so a
        # critical patient isn't blocked by the very
        # appointment they are about to displace.
        # ─────────────────────────────────────────

        existing_patient_booking = db.query(
            Appointment
        ).filter(
            Appointment.email == email,
            Appointment.doctor_name.ilike(
                f"%{doctor.name}%"
            )
        ).first()

        if existing_patient_booking:
            return (
                f"You already have an appointment "
                f"with Dr. {doctor.name}."
            )

        # ─────────────────────────────────────────
        # FIND CONFLICTING APPOINTMENT
        # ─────────────────────────────────────────

        booked_rows = db.query(Appointment).filter(
            Appointment.doctor_name.ilike(f"%{doctor_name}%")
        ).all()

        conflict_appt = None

        for row in booked_rows:

            try:
                existing_dt = datetime.strptime(
                    row.appointment_time,
                    "%Y-%m-%d %H:%M"
                )

                if abs(
                    (requested_dt - existing_dt).total_seconds()
                ) < 1800:

                    conflict_appt = row
                    break

            except:
                continue

        # ─────────────────────────────────────────
        # PRIORITY HANDLING
        # ─────────────────────────────────────────

        if conflict_appt:

            # CRITICAL PATIENT — bump the normal patient by one day
            if priority.upper() == "CRITICAL":

                old_dt = datetime.strptime(
                    conflict_appt.appointment_time,
                    "%Y-%m-%d %H:%M"
                )

                new_dt = old_dt + timedelta(days=1)

                conflict_appt.appointment_time = (
                    new_dt.strftime("%Y-%m-%d %H:%M")
                )

                db.commit()

                # Send reschedule email (best-effort)
                try:
                    send_reschedule_email(
                        email=conflict_appt.email,
                        patient_name=conflict_appt.patient_name,
                        doctor_name=conflict_appt.doctor_name,
                        old_time=old_dt.strftime(
                            "%A, %B %d, %Y at %I:%M %p"
                        ),
                        new_time=new_dt.strftime(
                            "%A, %B %d, %Y at %I:%M %p"
                        )
                    )

                except:
                    pass

            # NORMAL PATIENT — slot is taken, reject
            else:
                return (
                    f"Sorry, Dr. {doctor.name} already has "
                    f"an appointment at this time."
                )

        # ─────────────────────────────────────────
        # CREATE APPOINTMENT
        # ─────────────────────────────────────────

        appt = Appointment(
            patient_name=patient_name,
            doctor_name=doctor.name,
            appointment_time=requested_dt.strftime(
                "%Y-%m-%d %H:%M"
            ),
            email=email,
            priority=priority.upper()   # BUG FIX: was missing, always saved as NULL
        )

        db.add(appt)

        db.commit()

        return (
            f"Appointment confirmed! "
            f"{patient_name} with Dr. {doctor.name} "
            f"on "
            f"{requested_dt.strftime('%A, %B %d, %Y at %I:%M %p')}."
        )

    except Exception as e:

        db.rollback()

        return f"Booking failed: {str(e)}"

    finally:
        db.close()