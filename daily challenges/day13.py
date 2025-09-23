import streamlit as st
from streamlit_lottie import st_lottie
import requests
import random
import time

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(page_title="RPS Showdown", page_icon="🪨", layout="wide")

# Load Google Fonts + CSS overrides
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Poppins:wght@700&display=swap" rel="stylesheet">
    <style>
    html, body { font-size: clamp(18px, 1.15vw + 14px, 20px); font-family: 'Inter', sans-serif; }
    h1 { font-family: 'Poppins', sans-serif; font-size: clamp(44px, 6vw, 52px); font-weight: 700; }
    h2 { font-size: clamp(32px, 4vw, 36px); font-weight: 700; }
    h3 { font-size: clamp(24px, 3vw, 28px); font-weight: 600; }
    .stButton>button, .stDownloadButton>button {
        font-size: 18px !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: scale(1.05);
    }
    .score-big { font-size: clamp(40px, 6vw, 64px); font-weight: 800; line-height: 1; }
    .chip { font-size: 16px; padding: 6px 10px; border-radius: 999px; background: #2B8CFF20; }
    [data-testid="stMarkdownContainer"] p { font-size: 18px; }
    :root {
      --primary: #2B8CFF; --success: #00C781; --danger: #FF4D4F; --text: #0F172A; --bg: #0B1220;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------
# Asset Loading
# ---------------------------------------------------
@st.cache_data(show_spinner=False)
def load_lottie(url: str):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None

ASSETS = {
    "rock": load_lottie("https://assets6.lottiefiles.com/private_files/lf30_rock.json"),
    "paper": load_lottie("https://assets2.lottiefiles.com/packages/lf20_paper.json"),
    "scissors": load_lottie("https://assets7.lottiefiles.com/packages/lf20_scissors.json"),
}

# ---------------------------------------------------
# Init Session State
# ---------------------------------------------------
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.target_games = 0
    st.session_state.current_round = 0
    st.session_state.player_score = 0
    st.session_state.computer_score = 0
    st.session_state.ties = 0
    st.session_state.history = []
    st.session_state.player_choice = None
    st.session_state.computer_choice = None
    st.session_state.revealed = False

# ---------------------------------------------------
# Helpers
# ---------------------------------------------------
CHOICES = ["Rock", "Paper", "Scissors"]

def get_outcome(player, computer):
    if player == computer:
        return "Tie"
    wins = {
        "Rock": "Scissors",
        "Paper": "Rock",
        "Scissors": "Paper"
    }
    if wins[player] == computer:
        return "Win"
    return "Lose"

def reset_match():
    st.session_state.started = False
    st.session_state.target_games = 0
    st.session_state.current_round = 0
    st.session_state.player_score = 0
    st.session_state.computer_score = 0
    st.session_state.ties = 0
    st.session_state.history = []
    st.session_state.player_choice = None
    st.session_state.computer_choice = None
    st.session_state.revealed = False

def reset_round():
    st.session_state.player_choice = None
    st.session_state.computer_choice = None
    st.session_state.revealed = False

def play_round(player_choice):
    st.session_state.player_choice = player_choice
    st.session_state.computer_choice = None
    st.session_state.revealed = False

    # suspense delay
    time.sleep(0.5)
    comp_choice = random.choice(CHOICES)
    st.session_state.computer_choice = comp_choice
    st.session_state.revealed = True

    outcome = get_outcome(player_choice, comp_choice)

    if outcome == "Win":
        st.session_state.player_score += 1
    elif outcome == "Lose":
        st.session_state.computer_score += 1
    else:
        st.session_state.ties += 1

    st.session_state.current_round += 1

    st.session_state.history.append({
        "round": st.session_state.current_round,
        "player": player_choice,
        "computer": comp_choice,
        "outcome": outcome,
        "player_score": st.session_state.player_score,
        "computer_score": st.session_state.computer_score,
        "ties": st.session_state.ties,
    })

# ---------------------------------------------------
# UI Rendering
# ---------------------------------------------------
def render_header():
    st.title("🪨 Rock–Paper–Scissors Showdown ✂️")

    if st.session_state.started:
        progress = st.session_state.current_round / st.session_state.target_games
        st.progress(progress)
        st.markdown(
            f"**Round {st.session_state.current_round + 1} of {st.session_state.target_games}**"
        )

        cols = st.columns(3)
        cols[0].markdown(f"👤 Player: <span class='score-big'>{st.session_state.player_score}</span>", unsafe_allow_html=True)
        cols[1].markdown(f"🤖 Computer: <span class='score-big'>{st.session_state.computer_score}</span>", unsafe_allow_html=True)
        cols[2].markdown(f"🤝 Ties: <span class='score-big'>{st.session_state.ties}</span>", unsafe_allow_html=True)

def render_board():
    if not st.session_state.started:
        return

    # game board layout
    left, mid, right = st.columns([4,2,4])

    with left:
        st.subheader("You")
        if st.session_state.player_choice:
            choice = st.session_state.player_choice.lower()
            if ASSETS[choice]:
                st_lottie(ASSETS[choice], height=200, key="player_anim")
            else:
                st.markdown(f"### {st.session_state.player_choice}")
        else:
            st.info("Pick Rock, Paper, or Scissors")

    with mid:
        if st.session_state.revealed:
            outcome = get_outcome(st.session_state.player_choice, st.session_state.computer_choice)
            if outcome == "Win":
                st.success("You Win 🎉")
            elif outcome == "Lose":
                st.error("You Lose 💀")
            else:
                st.warning("It's a Tie 🤝")
        else:
            st.markdown("### ❓")

    with right:
        st.subheader("Computer")
        if st.session_state.revealed and st.session_state.computer_choice:
            choice = st.session_state.computer_choice.lower()
            if ASSETS[choice]:
                st_lottie(ASSETS[choice], height=200, key="comp_anim")
            else:
                st.markdown(f"### {st.session_state.computer_choice}")
        else:
            st.info("...waiting")

    if st.session_state.current_round < st.session_state.target_games:
        st.markdown("### Make your move:")
        btn_cols = st.columns(3)
        for i, choice in enumerate(CHOICES):
            if btn_cols[i].button(choice, key=f"btn_{choice}"):
                play_round(choice)
    else:
        # match complete
        if st.session_state.player_score > st.session_state.computer_score:
            st.success("🏆 You won the match!")
            st.balloons()
        elif st.session_state.player_score < st.session_state.computer_score:
            st.error("🤖 Computer won the match!")
        else:
            st.warning("🤝 It's a draw overall!")

        if st.button("Play Again"):
            reset_match()

def render_history():
    if st.session_state.history:
        st.subheader("📜 Round History")
        st.table(st.session_state.history)

def render_footer():
    st.markdown("---")
    st.caption("Animations © LottieFiles (open-source). Built with ❤️ using Streamlit.")

# ---------------------------------------------------
# App Flow
# ---------------------------------------------------
render_header()

if not st.session_state.started:
    st.subheader("Configure Match")
    target = st.number_input("How many games to play?", min_value=3, max_value=50, value=5, step=1)
    if st.button("Start Match"):
        st.session_state.started = True
        st.session_state.target_games = target

else:
    render_board()
    render_history()

render_footer()
