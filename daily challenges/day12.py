# streamlit_app.py

# ======================================================================================
# INSTALL & RUN
#
# This is a single-file Streamlit app. To run it:
#
# 1. Install/upgrade Streamlit:
#    pip install --upgrade streamlit
#
# 2. Run the app from your terminal:
#    streamlit run streamlit_app.py
#
# NOTE: This app uses injected CSS to enforce larger, more readable fonts and a
# custom modern theme, overriding Streamlit's default smaller typography.
# ======================================================================================

import streamlit as st
import random
import time
from typing import List, Tuple, Optional, Dict, Set

# --- Page Configuration ---
st.set_page_config(
    page_title="Tic-Tac-Toe ❌⭕",
    page_icon="❌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Modern UI/UX ---
# This CSS block is crucial for achieving the desired look and feel.
# It overrides default Streamlit styles for a polished, modern, and
# responsive design with large, comfortable typography.
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

:root {
    /* Modern Light Theme Color Palette */
    --bg: #f8fafc;
    --card: #ffffff;
    --text: #0f172a;
    --muted: #64748b;
    --primary: #3b82f6; /* A calmer blue */
    --accent: #0ea5e9;
    --win: #22c55e;
    --loss: #ef4444;
    --draw: #eab308;
    --grid: #e2e8f0;

    /* Shadows & Borders */
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    --border-radius-sm: 0.375rem; /* 6px */
    --border-radius-md: 0.5rem;   /* 8px */
    --border-radius-lg: 0.75rem;  /* 12px */
}

/* Base styles for a larger, more readable typography */
html, body, .stApp {
    font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    font-size: clamp(18px, 2.2vw, 22px); /* Responsive base font size */
    line-height: 1.5;
    color: var(--text);
    background-color: var(--bg);
}

/* Override Streamlit's default small header fonts */
h1 { font-size: clamp(2.5rem, 5vw, 3.5rem); font-weight: 800; }
h2 { font-size: clamp(1.75rem, 4vw, 2.5rem); font-weight: 800; }
h3 { font-size: clamp(1.25rem, 3vw, 1.75rem); font-weight: 600; }

/* Main app container styling */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Style all buttons for a premium feel */
.stButton > button {
    font-size: clamp(24px, 5vw, 36px) !important;
    min-height: 120px; /* Large, tappable grid buttons */
    width: 100%;
    font-weight: 800;
    letter-spacing: 0.4px;
    border-radius: var(--border-radius-lg);
    padding: 0.8rem 1rem;
    border: 2px solid var(--grid);
    background-color: var(--card);
    color: var(--primary);
    box-shadow: var(--shadow-sm);
    transition: transform 160ms ease, box-shadow 160ms ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
    border-color: var(--primary);
}

.stButton > button:active {
    transform: translateY(0);
    box-shadow: var(--shadow-sm);
}

/* Primary and secondary action buttons */
.stButton[kind="primary"] > button {
    background-color: var(--primary);
    color: white;
}
.stButton[kind="secondary"] > button {
    background-color: var(--muted);
    color: white;
    border-color: var(--muted);
}

/* Styling for the game grid tiles (non-button) */
.grid-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 120px;
    width: 100%;
    background-color: var(--card);
    border-radius: var(--border-radius-lg);
    font-size: clamp(3rem, 8vw, 5rem);
    font-weight: 800;
    border: 2px solid var(--grid);
    box-shadow: var(--shadow-sm);
}

/* Highlight for the winning line */
@keyframes pulse {
  0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
  70% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
  100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
}

.winning-cell {
    background: linear-gradient(135deg, rgba(34,197,94,.2), transparent);
    border: 2px solid var(--win);
    color: var(--win);
    box-shadow: var(--shadow-lg);
    animation: pulse 1.5s infinite;
}

/* Scoreboard and Status UI styles */
.scoreboard, .status-bar, .badge-container {
    background-color: var(--card);
    padding: 1.5rem;
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-md);
    text-align: center;
    margin-bottom: 2rem;
}

.status-bar {
    font-size: 1.25rem;
    font-weight: 600;
}
.status-win { color: var(--win); }
.status-draw { color: var(--draw); }
.status-turn { color: var(--text); }

/* Gamification badges */
.badge-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    justify-content: center;
}
.badge-chip {
    display: inline-block;
    padding: 0.5rem 1rem;
    background-color: var(--grid);
    border-radius: 9999px;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--muted);
    transition: transform 160ms ease;
}
.badge-chip:hover {
    transform: translateY(-2px);
}
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# --- Game State Initialization ---
def init_session_state():
    """Initializes all necessary keys in st.session_state if they don't exist."""
    defaults = {
        'board': [""] * 9,
        'current_player': "X",
        'starting_player': "X",
        'mode': "Two Players",
        'players': {"X": "Player 1", "O": "Player 2"},
        'scores': {"X": 0, "O": 0, "draws": 0},
        'game_over': False,
        'winner': None,
        'winning_cells': [],
        'turn_count': 0,
        'streak': {"Player 1": 0, "Player 2": 0, "CPU": 0},
        'badges': set(),
        'lock_ai': False,
        'swap_starter': True
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- Helper Functions ---

def new_match(reset_all: bool = False):
    """
    Resets the game for a new match.
    - If reset_all is True, resets scores, streaks, and badges.
    - If enabled, swaps the starting player for fairness.
    """
    if st.session_state.swap_starter and not st.session_state.game_over:
         # Only toggle if a game wasn't completed
         pass
    elif st.session_state.swap_starter:
        st.session_state.starting_player = "O" if st.session_state.starting_player == "X" else "X"

    st.session_state.board = [""] * 9
    st.session_state.current_player = st.session_state.starting_player
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.winning_cells = []
    st.session_state.turn_count = 0
    st.session_state.lock_ai = False

    if reset_all:
        st.session_state.scores = {"X": 0, "O": 0, "draws": 0}
        st.session_state.badges = set()
        st.session_state.streak = {name: 0 for name in st.session_state.streak}
        st.session_state.starting_player = "X"
        st.session_state.current_player = "X"


def check_winner(board: List[str]) -> Tuple[Optional[str], Optional[List[int]]]:
    """
    Checks for a winner on the board.
    Returns: A tuple of (winner_mark, winning_indices) or (None, None).
    """
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]             # Diagonals
    ]
    for line in lines:
        a, b, c = line
        if board[a] and board[a] == board[b] == board[c]:
            return board[a], line
    return None, None

def award_badges(winner_name: str, winning_cells: List[int], turn_count: int):
    """Awards badges based on game events."""
    badges = st.session_state.badges
    # First Win
    if "🎉 First Win" not in badges:
        badges.add("🎉 First Win")
    # Three-peat
    if st.session_state.streak.get(winner_name, 0) >= 3:
        badges.add("🥇 Three-peat")
    # Corner Start
    corners = {0, 2, 6, 8}
    if len(set(winning_cells) & corners) >= 2 and turn_count <= 5:
        badges.add("🧠 Corner Strategy")

    st.session_state.badges = badges

def update_streaks(winner_mark: Optional[str]):
    """Updates win streaks for players."""
    if winner_mark:
        winner_name = st.session_state.players[winner_mark]
        loser_mark = "O" if winner_mark == "X" else "X"
        loser_name = st.session_state.players[loser_mark]

        st.session_state.streak[winner_name] = st.session_state.streak.get(winner_name, 0) + 1
        if st.session_state.mode == "Two Players":
            st.session_state.streak[loser_name] = 0
    else: # Draw
        for name in st.session_state.streak:
             st.session_state.streak[name] = 0

def make_move(index: int):
    """Handles a player making a move."""
    if not st.session_state.board[index] and not st.session_state.game_over:
        player = st.session_state.current_player
        st.session_state.board[index] = player
        st.session_state.turn_count += 1

        winner, winning_line = check_winner(st.session_state.board)

        if winner:
            st.session_state.game_over = True
            st.session_state.winner = winner
            st.session_state.winning_cells = winning_line
            st.session_state.scores[winner] += 1
            winner_name = st.session_state.players[winner]
            update_streaks(winner)
            award_badges(winner_name, winning_line, st.session_state.turn_count)
            st.balloons()
        elif st.session_state.turn_count == 9:
            st.session_state.game_over = True
            st.session_state.winner = "Draw"
            st.session_state.scores["draws"] += 1
            update_streaks(None)
            st.snow()
        else:
            # Switch player
            st.session_state.current_player = "O" if player == "X" else "X"
            # If it's now the AI's turn, lock it for the AI move
            if st.session_state.mode == "Play vs Computer" and st.session_state.current_player == st.session_state.cpu_player:
                st.session_state.lock_ai = True

def ai_move():
    """Performs a random move for the computer."""
    time.sleep(random.uniform(0.3, 0.6)) # Simulate thinking
    empty_cells = [i for i, val in enumerate(st.session_state.board) if val == ""]
    if empty_cells:
        move = random.choice(empty_cells)
        make_move(move)
    st.session_state.lock_ai = False # Unlock after moving
    st.rerun()

# --- App Initialization ---
init_session_state()

# --- Sidebar UI for Game Configuration ---
with st.sidebar:
    st.header("Game Settings")

    st.radio(
        "Select Game Mode",
        ["Two Players", "Play vs Computer"],
        key='mode',
        on_change=new_match,
        args=(True,) # Reset everything on mode change
    )

    st.divider()

    player1_name = st.text_input("Player X Name", value=st.session_state.players['X'])
    if st.session_state.mode == "Two Players":
        player2_name = st.text_input("Player O Name", value=st.session_state.players['O'])
    else:
        player2_name = "CPU"
        st.text_input("Player O Name", value=player2_name, disabled=True)

    # Update player names and streaks dictionary
    st.session_state.players = {"X": player1_name, "O": player2_name}
    current_streaks = st.session_state.streak
    st.session_state.streak = {
        player1_name: current_streaks.get(st.session_state.players['X'], 0),
        player2_name: current_streaks.get(st.session_state.players['O'], 0)
    }


    # Determine CPU player mark
    st.session_state.human_player = 'X' # For simplicity, human is always X vs CPU
    st.session_state.cpu_player = 'O'

    st.selectbox(
        "Who Goes First?",
        ("X", "O"),
        key='starting_player',
        on_change=new_match
    )

    st.toggle(
        "Swap starting player after each match",
        value=True,
        key='swap_starter'
    )

    st.divider()
    st.header("Game Controls")
    st.button("✨ New Match", on_click=new_match, use_container_width=True)
    st.button("💣 Reset All", on_click=new_match, args=(True,), type="primary", use_container_width=True)

    # Optional: How to create a config.toml
    with st.expander("🎨 Want a permanent dark theme?"):
        st.code("""
# Create a file at .streamlit/config.toml
# and add these lines:

[theme]
base="dark"
primaryColor="#22c55e"
backgroundColor="#0f172a"
secondaryBackgroundColor="#1e293b"
textColor="#e2e8f0"
font="sans serif"
        """, language="toml")


# --- Main Game UI ---
st.title("Tic-Tac-Toe ❌⭕")

# --- Scoreboard & Badges ---
score_cols = st.columns(3)
with score_cols[0]:
    st.metric(
        label=f"🟢 {st.session_state.players['X']}'s Wins",
        value=st.session_state.scores['X']
    )
with score_cols[1]:
    st.metric(
        label="🟡 Draws",
        value=st.session_state.scores['draws']
    )
with score_cols[2]:
    st.metric(
        label=f"🔵 {st.session_state.players['O']}'s Wins",
        value=st.session_state.scores['O']
    )

# Display streaks if they are > 0
streak_text_parts = []
for player_name, streak_count in st.session_state.streak.items():
    if streak_count > 0:
        streak_text_parts.append(f"**{player_name}**: 🔥 {streak_count}-win streak!")

if streak_text_parts:
    st.markdown(" &nbsp; • &nbsp; ".join(streak_text_parts), unsafe_allow_html=True)


if st.session_state.badges:
    st.subheader("🏆 Achievements")
    badge_html = "<div class='badge-container'>"
    for badge in sorted(list(st.session_state.badges)):
        badge_html += f"<div class='badge-chip' title='{badge}'>{badge}</div>"
    badge_html += "</div>"
    st.markdown(badge_html, unsafe_allow_html=True)


st.write("---")

# --- Game Board Rendering ---
board = st.session_state.board
game_over = st.session_state.game_over
winning_cells = st.session_state.winning_cells

for i in range(3):
    cols = st.columns(3)
    for j in range(3):
        index = i * 3 + j
        cell_value = board[index]
        is_winning_cell = index in winning_cells

        # Determine cell class for styling
        cell_class = "grid-cell"
        if is_winning_cell:
            cell_class += " winning-cell"

        with cols[j]:
            if game_over or cell_value:
                # Display filled or post-game cells as styled markdown
                symbol = "❌" if cell_value == "X" else "⭕" if cell_value == "O" else ""
                st.markdown(
                    f"<div class='{cell_class}'>{symbol}</div>",
                    unsafe_allow_html=True
                )
            else:
                # Display empty, playable cells as buttons
                st.button(
                    " ", # Visually empty, but takes space
                    key=f"cell-{index}",
                    on_click=make_move,
                    args=(index,),
                    use_container_width=True,
                    # Disable if it's the AI's turn
                    disabled=st.session_state.mode == "Play vs Computer" and st.session_state.current_player == st.session_state.cpu_player
                )

st.write("---")

# --- Status Bar ---
status_container = st.container()
with status_container:
    if game_over:
        if st.session_state.winner == "Draw":
            st.info("🎨 It's a draw!", icon="🤝")
        else:
            winner_name = st.session_state.players[st.session_state.winner]
            st.success(f"🎉 **{winner_name}** wins the match!", icon="🏆")
    else:
        current_player_name = st.session_state.players[st.session_state.current_player]
        st.info(f"⏳ It's **{current_player_name}**'s turn ({st.session_state.current_player})", icon="👉")


# --- AI Move Logic ---
# This block runs at the end of the script execution.
# If the AI needs to move, it will do so, then trigger a rerun to show the move.
if (
    st.session_state.mode == "Play vs Computer"
    and st.session_state.current_player == st.session_state.cpu_player
    and not st.session_state.game_over
    and st.session_state.lock_ai
):
    ai_move()