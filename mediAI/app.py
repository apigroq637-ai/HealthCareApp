import os
import uuid

import streamlit as st

from auth import init_auth_tables, sign_up, log_in
from agent_router import handle_query
from database import init_db

from db_helper import (
    get_all_appointments,
    get_patient_appointments,
    get_patient_summary_data
)

from summarizer_agent import run_summarizer
from rag.ingest import ingest_report
from rag.retriever import retrieve_patient_context

# Initialise DB tables on cold start
init_db()
init_auth_tables()

st.set_page_config(page_title="MediAI System", layout="centered")

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

for key, default in [
    ("user", None),
    ("messages", []),
    ("doctor_page", "list"),
    ("selected_patient", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────

def _logout():
    if st.sidebar.button("🚪 Log Out"):
        st.session_state.update({
            "user": None,
            "messages": [],
            "doctor_page": "list",
            "selected_patient": None
        })
        st.rerun()


# ─────────────────────────────────────────────
# AUTH SCREEN
# ─────────────────────────────────────────────

def render_auth():
    st.title("🏥 MediAI System")

    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

    with tab_login:
        role = st.selectbox("Role", ["patient", "doctor"], key="login_role")
        user_id = st.text_input("User ID", key="login_user_id")
        pw = st.text_input("Password", type="password", key="login_password")

        if st.button("Log In", key="login_button"):
            result = log_in(user_id.strip(), pw, role)
            if result["success"]:
                st.session_state["user"] = result
                st.rerun()
            else:
                st.error(result["error"])

    with tab_signup:
        role = st.selectbox("Signup Role", ["patient", "doctor"], key="signup_role")
        name = st.text_input("Full Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        specialization = ""
        available_time = ""

        if role == "doctor":
            specialization = st.text_input("Specialization", key="signup_specialization")
            available_time = st.text_input("Availability (e.g. 9 AM - 5 PM)", key="signup_availability")

        pw = st.text_input("Password", type="password", key="signup_password")
        pw2 = st.text_input("Confirm Password", type="password", key="signup_confirm_password")

        if st.button("Create Account", key="signup_button"):
            if pw != pw2:
                st.error("Passwords do not match.")
            elif not name or not email or not pw:
                st.error("All fields are required.")
            else:
                result = sign_up(
                    name=name, email=email, password=pw, role=role,
                    specialization=specialization, available_time=available_time
                )
                if result["success"]:
                    st.success(f"Account created! Your ID is {result['id']}")
                else:
                    st.error(result["error"])


# ─────────────────────────────────────────────
# PATIENT DASHBOARD
# ─────────────────────────────────────────────

def render_patient_dashboard():
    user = st.session_state["user"]

    st.sidebar.markdown(f"### 👤 {user['name']}")
    st.sidebar.markdown(f"**Email:** {user['email']}")
    _logout()

    st.title("🏥 Patient Portal")

    st.subheader("📋 My Appointments")
    appointments = get_patient_appointments(user["email"])
    if appointments:
        for appt in appointments:
            st.markdown(f"- **{appt['doctor']}** — {appt['time']}")
    else:
        st.info("No appointments yet.")

    st.markdown("---")
    st.subheader("📄 Upload Medical Reports")

    uploaded_file = st.file_uploader("Upload PDF medical reports", type=["pdf"])
    if uploaded_file:
        # Use /tmp for Railway compatibility
        os.makedirs("/tmp/uploads", exist_ok=True)
        unique_name = f"{uuid.uuid4()}.pdf"
        save_path = os.path.join("/tmp/uploads", unique_name)

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("Document uploaded")
        with st.container(border=True):
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown("📄")
            with col2:
                st.markdown(f"### {uploaded_file.name}")
                st.caption(f"Size: {round(uploaded_file.size / 1024, 2)} KB")

        with st.spinner("Processing report into RAG system..."):
            result = ingest_report(pdf_path=save_path, patient_email=user["email"])

        if result["success"]:
            st.success("🧠 RAG ingestion successful")
            st.metric(label="Chunks Stored", value=result["chunks"])
            st.info(f"File Stored: {result['filename']}")
        else:
            st.error(result["message"])

    st.markdown("---")
    st.subheader("💬 Medical Assistant")

    patient_ctx = f"[Patient: name={user['name']}, email={user['email']}]"

    for msg in st.session_state["messages"]:
        if msg.get("hidden"):
            continue
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Message"):
        if not st.session_state["messages"]:
            st.session_state["messages"].append({
                "role": "user", "content": patient_ctx, "hidden": True
            })

        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state["messages"]
        ]
        result = handle_query(prompt, history)
        output = result["output"]

        with st.chat_message("assistant"):
            st.markdown(output)

        st.session_state["messages"].append({"role": "assistant", "content": output})


# ─────────────────────────────────────────────
# DOCTOR DASHBOARD
# ─────────────────────────────────────────────

def render_doctor_appointments_list():
    st.title("📋 Appointments")
    user = st.session_state["user"]
    appointments = get_all_appointments(user["name"])

    if not appointments:
        st.info("No appointments.")
        return

    for appt in appointments:
        with st.container(border=True):
            priority = (appt.get("priority") or "NORMAL").upper()
            label = "🔴 CRITICAL" if priority == "CRITICAL" else "🟢 NORMAL"
            st.markdown(
                f"### {appt['patient_name']}\n\n"
                f"**Priority:** {label}\n\n"
                f"Doctor: {appt['doctor_name']}\n\n"
                f"Time: {appt['appointment_time']}"
            )
            if st.button("Summarize", key=appt["id"]):
                st.session_state["selected_patient"] = appt["email"]
                st.session_state["doctor_page"] = "detail"
                st.rerun()


def render_doctor_patient_detail():
    if st.button("← Back"):
        st.session_state["doctor_page"] = "list"
        st.rerun()

    email = st.session_state["selected_patient"]
    patient_data = get_patient_summary_data(email)

    st.title(f"🧑‍⚕️ {patient_data['patient_name']}")

    rag_context = retrieve_patient_context(
        email=email,
        query="Patient diagnoses, allergies, blood reports, scans, chronic diseases, laboratory findings"
    )

    with st.expander("📚 Retrieved RAG Context"):
        st.text(rag_context)

    with st.spinner("Generating summary..."):
        summary = run_summarizer(patient_data, rag_context)

    st.markdown(summary)


def render_doctor_dashboard():
    user = st.session_state["user"]
    st.sidebar.markdown(f"### 👨‍⚕️ Dr. {user['name']}")
    st.sidebar.markdown(f"**ID:** `{user['id']}`")
    st.sidebar.markdown("---")

    page_options = ["📋 Appointments", "🧑‍⚕️ Patient Detail"]
    current_index = 1 if st.session_state["doctor_page"] == "detail" else 0
    page = st.sidebar.radio("Dashboard", page_options, index=current_index, key="doctor_dashboard_radio")

    if page == "📋 Appointments":
        st.session_state["doctor_page"] = "list"
    else:
        st.session_state["doctor_page"] = "detail"

    _logout()

    if st.session_state["doctor_page"] == "list":
        render_doctor_appointments_list()
    else:
        render_doctor_patient_detail()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

user = st.session_state["user"]

if user is None:
    render_auth()
elif user["role"] == "patient":
    render_patient_dashboard()
elif user["role"] == "doctor":
    render_doctor_dashboard()
