import streamlit as st

st.set_page_config(page_title="Science Quiz 🧪", layout="centered")

# -------------------------------
# Quiz Questions (Fixed Order)
# -------------------------------
questions = [
    {"question": "What gas do humans exhale in large amounts?",
     "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"],
     "answer": "Carbon Dioxide"},
    {"question": "Which part of the plant makes food using sunlight?",
     "options": ["Root", "Stem", "Leaf", "Flower"],
     "answer": "Leaf"},
    {"question": "What is the chemical symbol for water?",
     "options": ["WO", "H2O", "O2", "HO2"],
     "answer": "H2O"},
    {"question": "What force pulls objects toward Earth?",
     "options": ["Magnetism", "Gravity", "Friction", "Inertia"],
     "answer": "Gravity"},
    {"question": "What organ in the human body pumps blood?",
     "options": ["Lungs", "Liver", "Heart", "Brain"],
     "answer": "Heart"},
    {"question": "Which planet is known as the Red Planet?",
     "options": ["Venus", "Mars", "Jupiter", "Mercury"],
     "answer": "Mars"},
    {"question": "What is the smallest unit of life?",
     "options": ["Tissue", "Organ", "Cell", "Molecule"],
     "answer": "Cell"},
    {"question": "Which gas is most abundant in Earth's atmosphere?",
     "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"],
     "answer": "Nitrogen"},
    {"question": "Which blood cells help fight infection?",
     "options": ["Red Blood Cells", "White Blood Cells", "Platelets", "Plasma"],
     "answer": "White Blood Cells"},
    {"question": "What energy source is produced by moving water?",
     "options": ["Solar Energy", "Wind Energy", "Hydroelectric Energy", "Geothermal Energy"],
     "answer": "Hydroelectric Energy"},
]

# -------------------------------
# Session State
# -------------------------------
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "answers" not in st.session_state:
    st.session_state.answers = [None] * len(questions)
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "name" not in st.session_state:
    st.session_state.name = ""

# -------------------------------
# Styles (Clean UI)
# -------------------------------
st.markdown(
    """
    <style>
    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Roboto', 'Helvetica Neue', sans-serif !important;
    }

    /* Title */
    h1 {
        font-size: 48px !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 25px !important;
    }

    /* Question text */
    .big-question {
        font-size: 32px !important;
        font-weight: 600 !important;
        margin: 20px 0 30px 0 !important;
        line-height: 1.4;
    }

    /* Options */
    .stRadio label {
        font-size: 22px !important;
        margin: 8px 0 !important;
    }

    /* Buttons */
    .stButton button {
        font-size: 20px !important;
        font-weight: 600 !important;
        padding: 10px 25px !important;
        border-radius: 8px !important;
        margin-top: 20px !important;
        border: none !important;
    }
    .stButton button:hover {
        opacity: 0.9 !important;
    }
    .back-btn button {background-color: orange !important; color: white !important;}
    .next-btn button {background-color: #1E88E5 !important; color: white !important;}
    .submit-btn button {background-color: green !important; color: white !important;}

    /* Input field */
    .stTextInput input {
        font-size: 18px !important;
        padding: 8px 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# Name input
# -------------------------------
if not st.session_state.name:
    st.session_state.name = st.text_input("Enter your name to start the quiz:")
    if not st.session_state.name:
        st.stop()

# -------------------------------
# Quiz Logic
# -------------------------------
if not st.session_state.quiz_submitted:
    idx = st.session_state.current_question
    q = questions[idx]

    # Question
    st.markdown(f"<p class='big-question'>Q{idx+1}: {q['question']}</p>", unsafe_allow_html=True)

    # Restore saved answer
    saved_answer = st.session_state.answers[idx]
    if saved_answer is not None:
        default_index = q["options"].index(saved_answer)
    else:
        default_index = None

    choice = st.radio(
        "Select your answer:",
        q["options"],
        index=default_index,
        key=f"radio_q{idx}",
        label_visibility="collapsed"
    )

    # Save answer
    if choice:
        st.session_state.answers[idx] = choice

    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if idx > 0:
            if st.button("⬅️ Back", key=f"back{idx}", help="Go to previous question"):
                st.session_state.current_question -= 1
                st.rerun()

    with col2:
        if idx < len(questions) - 1:
            if st.button("➡️ Next", key=f"next{idx}", help="Go to next question"):
                if st.session_state.answers[idx] is not None:
                    st.session_state.current_question += 1
                    st.rerun()
                else:
                    st.warning("⚠️ Please select an answer before proceeding.")

    with col3:
        if idx == len(questions) - 1:
            if st.button("✅ Submit Quiz", key="submit", help="Submit your quiz"):
                if st.session_state.answers[idx] is not None:
                    st.session_state.quiz_submitted = True
                    st.rerun()
                else:
                    st.warning("⚠️ Please select an answer before submitting.")

# -------------------------------
# Results
# -------------------------------
else:
    score = sum(
        1 for i, q in enumerate(questions) if st.session_state.answers[i] == q["answer"]
    )
    st.markdown("---")
    st.markdown(f"## Final Score: {score} / {len(questions)}")

    if score > 7:
        st.success(f"🎉 Congratulations, {st.session_state.name}! You're a Science Star! 🌟")
    else:
        st.warning(f"💪 Good try, {st.session_state.name}! Science is about learning. Reattempt and improve!")

    if st.button("🔄 Reattempt Quiz"):
        st.session_state.current_question = 0
        st.session_state.answers = [None] * len(questions)
        st.session_state.quiz_submitted = False
        st.rerun()
