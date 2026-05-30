from langchain.tools import tool


@tool
def clinical_triage(symptoms: str):
    """
    Maps symptoms to possible conditions and urgency level.
    Uses rule-based emergency keyword detection for clinical triage.
    """

    text = symptoms.lower()

    # ---------------------------
    # CRITICAL CONDITIONS
    # ---------------------------

    if "chest pain" in text and "left" in text:
        return {
            "risk_level": "CRITICAL",
            "possible_conditions": [
                "Myocardial infarction (heart attack)",
                "Acute coronary syndrome"
            ],
            "advice": "Seek emergency medical help immediately (call emergency services)."
        }

    if "shortness of breath" in text:
        return {
            "risk_level": "CRITICAL",
            "possible_conditions": [
                "Pulmonary embolism",
                "Asthma attack",
                "Heart failure"
            ],
            "advice": "Immediate emergency evaluation required."
        }

    if "sudden weakness" in text or "one side weakness" in text:
        return {
            "risk_level": "CRITICAL",
            "possible_conditions": [
                "Stroke (CVA)",
                "Transient ischemic attack (TIA)"
            ],
            "advice": "Call emergency services immediately."
        }

    if "slurred speech" in text:
        return {
            "risk_level": "CRITICAL",
            "possible_conditions": [
                "Stroke",
                "Neurological emergency"
            ],
            "advice": "Immediate hospital evaluation required."
        }

    if "loss of consciousness" in text:
        return {
            "risk_level": "CRITICAL",
            "possible_conditions": [
                "Cardiac arrest",
                "Seizure",
                "Severe hypoglycemia"
            ],
            "advice": "Emergency medical intervention required."
        }

    if "vomiting blood" in text:
        return {
            "risk_level": "CRITICAL",
            "possible_conditions": [
                "Upper gastrointestinal bleed",
                "Peptic ulcer rupture"
            ],
            "advice": "Emergency hospital admission required."
        }

    if "severe headache" in text and "sudden" in text:
        return {
            "risk_level": "CRITICAL",
            "possible_conditions": [
                "Brain hemorrhage",
                "Aneurysm rupture"
            ],
            "advice": "Immediate CT scan and emergency care required."
        }

    if "severe allergic reaction" in text or "anaphylaxis" in text:
        return {
            "risk_level": "CRITICAL",
            "possible_conditions": [
                "Anaphylactic shock"
            ],
            "advice": "Administer emergency treatment immediately (epinephrine required)."
        }

    if "sudden vision loss" in text:
        return {
            "risk_level": "CRITICAL",
            "possible_conditions": [
                "Retinal detachment",
                "Stroke"
            ],
            "advice": "Emergency ophthalmology/neurology evaluation required."
        }

    if "high fever" in text and "stiff neck" in text:
        return {
            "risk_level": "CRITICAL",
            "possible_conditions": [
                "Meningitis"
            ],
            "advice": "Immediate hospital admission required."
        }

    if "trauma" in text or "head injury" in text:
        return {
            "risk_level": "CRITICAL",
            "possible_conditions": [
                "Concussion",
                "Intracranial hemorrhage"
            ],
            "advice": "Urgent emergency imaging and evaluation required."
        }

    if "diabetic ketoacidosis" in text or "high blood sugar" in text:
        return {
            "risk_level": "CRITICAL",
            "possible_conditions": [
                "Diabetic ketoacidosis (DKA)"
            ],
            "advice": "Emergency insulin and hospital care required."
        }

    # ---------------------------
    # HIGH URGENCY CONDITIONS
    # ---------------------------

    if "seizure" in text:
        return {
            "risk_level": "HIGH",
            "possible_conditions": [
                "Epilepsy",
                "Brain injury",
                "Metabolic disorder"
            ],
            "advice": "Urgent neurological evaluation recommended."
        }

    if "severe abdominal pain" in text:
        return {
            "risk_level": "HIGH",
            "possible_conditions": [
                "Appendicitis",
                "Pancreatitis",
                "Bowel obstruction"
            ],
            "advice": "Urgent surgical evaluation recommended."
        }

    if "black stool" in text or "tarry stool" in text:
        return {
            "risk_level": "HIGH",
            "possible_conditions": [
                "Upper gastrointestinal bleeding"
            ],
            "advice": "Urgent gastroenterology assessment required."
        }

    if "palpitations" in text:
        return {
            "risk_level": "HIGH",
            "possible_conditions": [
                "Arrhythmia",
                "Anxiety",
                "Cardiac dysfunction"
            ],
            "advice": "Cardiac evaluation recommended."
        }

    if "persistent vomiting" in text:
        return {
            "risk_level": "HIGH",
            "possible_conditions": [
                "Gastroenteritis",
                "Bowel obstruction",
                "Infection"
            ],
            "advice": "Medical assessment recommended urgently."
        }

    if "dehydration" in text or "heatstroke" in text:
        return {
            "risk_level": "HIGH",
            "possible_conditions": [
                "Severe dehydration",
                "Heatstroke"
            ],
            "advice": "Immediate rehydration and medical evaluation required."
        }

    if "chest tightness" in text:
        return {
            "risk_level": "HIGH",
            "possible_conditions": [
                "Acute coronary syndrome",
                "Angina",
                "Respiratory issue"
            ],
            "advice": "Urgent cardiac evaluation required."
        }

    if "back pain" in text and "numbness" in text:
        return {
            "risk_level": "HIGH",
            "possible_conditions": [
                "Spinal cord compression",
                "Nerve impingement"
            ],
            "advice": "Urgent neurological evaluation required."
        }

    if "dizziness" in text and "palpitations" in text:
        return {
            "risk_level": "HIGH",
            "possible_conditions": [
                "Arrhythmia",
                "Orthostatic hypotension"
            ],
            "advice": "Cardiac assessment recommended."
        }

    # ---------------------------
    # DEFAULT CASE
    # ---------------------------

    return {
        "risk_level": "LOW",
        "possible_conditions": [
            "Non-specific symptoms",
            "Mild viral illness",
            "Minor fatigue-related issues"
        ],
        "advice": "Routine outpatient consultation recommended."
    }