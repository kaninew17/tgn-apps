# The following code block is the corrected version of the Streamlit Snake game.
# It addresses the threading issue by using Streamlit's native rerun mechanism
# for the game loop, making it safe and stable.

import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import time
import random
import json
import os
import math
import numpy as np
import base64
import io
import threading

# -----------------------
# Constants & Defaults
# -----------------------
HIGH_SCORE_FILE = ".snake_highscore.json"
DEFAULT_GRID = (20, 20)
DEFAULT_CELL_DESKTOP = 24
DEFAULT_CELL_MOBILE = 18
MIN_TOUCH_TARGET = 44  # px
LEVEL_UP_FOOD = 5
BADGE_THRESHOLDS = [5, 10, 20]
BASE_TICK_MS = 160  # normal speed
SPEED_PRESETS = {
    "Slow": 240,
    "Normal": 160,
    "Fast": 100,
}
FONT_IMPORT = "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap"

# -----------------------
# Utility Functions
# -----------------------


def clamp(n, a, b):
    return max(a, min(b, n))


def now_ms():
    return int(time.time() * 1000)


# -----------------------
# State Initialization & Persistence
# -----------------------
def load_high_score():
    """Attempt to read high score from disk. Return int or 0."""
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return int(data.get("high_score", 0))
    except Exception:
        # silently ignore file errors
        pass
    return 0


def save_high_score(value):
    """Attempt to save high score to disk. Fails silently."""
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"high_score": int(value)}, f)
    except Exception:
        # silently ignore
        pass


def init_state():
    """Initialize session_state keys if missing."""
    ss = st.session_state
    ss.setdefault("grid_size", DEFAULT_GRID)  # (rows, cols)
    ss.setdefault("cell_size", DEFAULT_CELL_DESKTOP)
    ss.setdefault("snake", None)
    ss.setdefault("direction", (0, 1))  # moving right initially (dr, dc)
    ss.setdefault("next_direction", (0, 1))
    ss.setdefault("food_pos", None)
    ss.setdefault("score", 0)
    ss.setdefault("high_score", load_high_score())
    ss.setdefault("level", 1)
    ss.setdefault("running", False)
    ss.setdefault("game_over", False)
    ss.setdefault("tick_ms", BASE_TICK_MS)
    ss.setdefault("last_update_ts", now_ms())
    ss.setdefault("rng_state", None)
    ss.setdefault("sound_on", True)
    ss.setdefault("achievement_badges", set())
    ss.setdefault("steps", 0)
    ss.setdefault("pulse_frame", 0)
    ss.setdefault("streak", 0)
    ss.setdefault("confetti_frame", 0)
    ss.setdefault("auto_focus_key", 0)  # used to force focus in component
    # For simple audio playback via HTML component: store base64 or None
    ss.setdefault("eat_sound_b64", _embed_default_eat_sound_b64())
    ss.setdefault("death_sound_b64", _embed_default_death_sound_b64())


def reset_game(preserve_high_score=True):
    """Reset the run-specific state but preserve high score if requested."""
    ss = st.session_state
    rows, cols = ss["grid_size"]
    mid_r, mid_c = rows // 2, cols // 2
    initial_snake = [(mid_r, mid_c - i) for i in range(3)][::-1]  # head at end
    ss["snake"] = initial_snake[:]  # list of (r, c)
    ss["direction"] = (0, 1)
    ss["next_direction"] = (0, 1)
    ss["food_pos"] = place_food(initial_snake, ss["grid_size"])
    ss["score"] = 0
    ss["level"] = 1
    ss["running"] = False
    ss["game_over"] = False
    ss["tick_ms"] = BASE_TICK_MS
    ss["last_update_ts"] = now_ms()
    ss["steps"] = 0
    ss["pulse_frame"] = 0
    ss["streak"] = 0
    ss["confetti_frame"] = 0
    ss["achievement_badges"] = set()
    if preserve_high_score:
        ss.setdefault("high_score", load_high_score())
    else:
        ss["high_score"] = 0


# -----------------------
# Game Logic
# -----------------------
def place_food(snake, grid_size):
    """Place food at random free cell."""
    rows, cols = grid_size
    occupied = set(snake)
    free = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in occupied]
    if not free:
        return None
    return random.choice(free)


def step():
    """Advance the game one tick. Returns dict with 'ate', 'collision' flags."""
    ss = st.session_state
    if ss["game_over"]:
        return {"ate": False, "collision": True}

    snake = ss["snake"]
    dirr = ss["direction"]
    head = snake[-1]
    new_head = (head[0] + dirr[0], head[1] + dirr[1])
    rows, cols = ss["grid_size"]

    # wall collision
    if not (0 <= new_head[0] < rows and 0 <= new_head[1] < cols):
        ss["game_over"] = True
        ss["running"] = False
        return {"ate": False, "collision": True}

    # self collision
    if new_head in snake:
        ss["game_over"] = True
        ss["running"] = False
        return {"ate": False, "collision": True}

    ate = False
    if new_head == ss["food_pos"]:
        ate = True
        snake.append(new_head)  # grow
        ss["score"] += 1
        ss["steps"] += 1
        ss["streak"] += 1
        # place new food
        ss["food_pos"] = place_food(snake, ss["grid_size"])
        # level up every LEVEL_UP_FOOD
        new_level = 1 + (ss["score"] // LEVEL_UP_FOOD)
        if new_level != ss["level"]:
            ss["level"] = new_level
            # speed up slightly but clamp minimum tick
            ss["tick_ms"] = max(60, int(ss["tick_ms"] * 0.92))
            ss["confetti_frame"] = 6  # show confetti for a few frames
        # badges
        for t in BADGE_THRESHOLDS:
            if ss["score"] >= t:
                ss["achievement_badges"].add(t)
    else:
        # move normally: pop head, push new head
        snake.pop(0)
        snake.append(new_head)
        ss["steps"] += 1
        ss["streak"] = 0  # reset streak on non-food move

    # update high score
    if ss["score"] > ss.get("high_score", 0):
        ss["high_score"] = ss["score"]
        try:
            save_high_score(ss["high_score"])
        except Exception:
            pass

    # pulse frame increment
    ss["pulse_frame"] = (ss["pulse_frame"] + 1) % 30
    return {"ate": ate, "collision": False}


# -----------------------
# Rendering
# -----------------------
def draw_board(grid_size, snake, food_pos, cell_size=24, pulse_frame=0, confetti=False):
    """
    Draw the board to a PIL image and return it (RGBA).
    - rounded snake segments, brighter head, subtle grid lines.
    - pulsing food effect: alternate food color/brightness using pulse_frame.
    - confetti: if True, overlay emoji-like colored circles for one frame.
    """
    rows, cols = grid_size
    width = cols * cell_size
    height = rows * cell_size

    # Create base image
    img = Image.new("RGBA", (width, height), (14, 17, 23, 255))
    draw = ImageDraw.Draw(img)

    # soft grid lines
    line_color = (18, 23, 29, 255)
    for r in range(rows + 1):
        y = r * cell_size + 0.5
        draw.line([(0, y), (width, y)], fill=line_color, width=1)
    for c in range(cols + 1):
        x = c * cell_size + 0.5
        draw.line([(x, 0), (x, height)], fill=line_color, width=1)

    # snake body gradient greens
    if snake:
        grad_start = np.array([36, 180, 100])
        grad_end = np.array([14, 102, 71])
        L = len(snake)
        for i, (r, c) in enumerate(snake):
            t = i / max(1, L - 1)
            color = tuple((grad_start * (1 - t) + grad_end * t).astype(int)) + (255,)
            x0 = c * cell_size + 2
            y0 = r * cell_size + 2
            x1 = (c + 1) * cell_size - 2
            y1 = (r + 1) * cell_size - 2
            # rounded rectangle (ellipse corners)
            draw.rounded_rectangle([x0, y0, x1, y1], radius=int(cell_size / 4), fill=color)

        # head highlight
        head = snake[-1]
        hx0 = head[1] * cell_size + 1
        hy0 = head[0] * cell_size + 1
        hx1 = (head[1] + 1) * cell_size - 1
        hy1 = (head[0] + 1) * cell_size - 1
        draw.rounded_rectangle([hx0, hy0, hx1, hy1], radius=int(cell_size / 3),
                               fill=(76, 255, 169, 255), outline=(255, 255, 255, 80), width=2)

    # pulsing food
    if food_pos:
        fr, fc = food_pos
        pulse = (math.sin(pulse_frame / 3.0) + 1) / 2.0  # 0..1
        amber = (245, 158, 11)
        amber_glow = (255, 199, 79)
        color = tuple(int(amber[i] * (1 - pulse) + amber_glow[i] * pulse) for i in range(3)) + (255,)
        x0 = fc * cell_size + 3
        y0 = fr * cell_size + 3
        x1 = (fc + 1) * cell_size - 3
        y1 = (fr + 1) * cell_size - 3
        draw.ellipse([x0, y0, x1, y1], fill=color)
        # small sparkle
        sx = (fc + 0.35) * cell_size
        sy = (fr + 0.25) * cell_size
        draw.ellipse([sx, sy, sx + cell_size * 0.12, sy + cell_size * 0.12], fill=(255, 230, 170, 220))

    # confetti
    if confetti:
        for i in range(12):
            rx = random.randint(0, width)
            ry = random.randint(0, height)
            rr = random.randint(3, max(4, cell_size // 3))
            color = tuple([random.randint(120, 255) for _ in range(3)]) + (220,)
            draw.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=color)

    # subtle vignette
    vign = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vign)
    vdraw.rectangle([0, 0, width, height], fill=(0, 0, 0, 0))
    # composite
    img = Image.alpha_composite(img, vign)

    return img


# -----------------------
# Input Handling
# -----------------------
def handle_direction_input(key_char):
    """
    Map keyboard character to directions and set next_direction if valid.
    Prevent immediate 180-degree reversal if snake length > 1.
    """
    mapping = {
        "w": (-1, 0),
        "a": (0, -1),
        "s": (1, 0),
        "d": (0, 1),
        " ": "TOGGLE",  # space toggles start/pause
    }
    ss = st.session_state
    char = (key_char or "").lower()
    if char not in mapping:
        return

    if mapping[char] == "TOGGLE":
        ss["running"] = not ss["running"]
        ss["auto_focus_key"] += 1
        return

    nd = mapping[char]
    # prevent 180-degree reversal if length > 1
    cur = ss["direction"]
    if len(ss["snake"]) > 1 and (nd[0] == -cur[0] and nd[1] == -cur[1]):
        return
    ss["next_direction"] = nd


# -----------------------
# Sound (embedded base64 small beeps)
# -----------------------
def _embed_default_eat_sound_b64():
    # generate a tiny beep via sine wave? For simplicity use a short base64 wav precomputed small sound.
    # Here: tiny 0.05s beep (sampled) base64. If you want to replace, put your own base64 string.
    # NOTE: This is a short 8-bit PCM placeholder; it's small but sufficient for a click.
    return ("UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAABErAAABAAgAZGF0YQAAAAA=")


def _embed_default_death_sound_b64():
    return ("UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAABErAAABAAgAZGF0YQAAAAA=")


def play_sound_html(b64):
    """Return an HTML snippet that plays a base64 wav if sound_on is True. The HTML auto-plays with JS call."""
    if not b64:
        return ""
    html = f"""
    <audio id="sfx" preload="auto">
      <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    </audio>
    <script>
      const el = document.getElementById('sfx');
      try {{
        el.currentTime = 0;
        el.play();
      }} catch(e) {{
        // ignore autoplay errors
      }}
    </script>
    """
    return html


# -----------------------
# Components / Small Helpers
# -----------------------
def _inject_global_css():
    """Inject the large-font CSS, color palette, and micro-interactions."""
    css = f"""
    <style>
    @import url('{FONT_IMPORT}');
    :root {{
      --bg: #0B0F14;
      --fg: #E6EDF3;
      --muted: #9aa7b2;
      --accent: #10B981;
      --food: #F59E0B;
      --danger: #EF4444;
      --base-font-size: 20px;
    }}
    @media (max-width: 768px) {{
      :root {{ --base-font-size: 18px; }}
    }}
    html, body, .stApp {{
      font-family: 'Poppins', system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif !important;
      background: var(--bg) !important;
      color: var(--fg) !important;
      font-size: var(--base-font-size) !important;
      line-height: 1.5 !important;
    }}
    /* Headers */
    h1 {{ font-size: 2.2rem; margin-bottom: 0.25rem; }}
    h2 {{ font-size: 1.6rem; margin-bottom: 0.25rem; }}
    /* Buttons */
    .big-btn > button, .big-btn button {{
      min-height: 48px !important;
      height: 48px;
      font-size: 1rem !important;
      border-radius: 12px !important;
      transition: transform 150ms ease, filter 120ms ease;
    }}
    .big-btn > button:hover, .big-btn button:hover {{ transform: translateY(-1px) scale(1.01); filter: brightness(1.04); }}
    .big-btn > button:active, .big-btn button:active {{ transform: translateY(0px) scale(0.99); }}
    /* Focus ring */
    .stButton>button:focus, .stTextInput>div>input:focus {{
      outline: 3px solid rgba(16,185,129,0.22);
      outline-offset: 3px;
    }}
    /* Sidebar tweaks */
    [data-testid="stSidebar"] {{
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      color: var(--fg);
    }}
    /* Small metadata */
    .meta-label {{ color: var(--muted); font-size: 0.95rem; }}
    /* Toast / overlay */
    .snake-toast {{
      position: absolute;
      left: 50%;
      transform: translateX(-50%);
      top: 8%;
      background: linear-gradient(90deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
      padding: 10px 14px;
      border-radius: 12px;
      font-weight: 600;
      z-index: 9999;
      box-shadow: 0 6px 20px rgba(0,0,0,0.6);
      backdrop-filter: blur(6px);
      color: var(--fg);
    }}
    /* Small badge */
    .badge {{
      display:inline-block; padding:6px 10px; border-radius:999px; background: rgba(255,255,255,0.04);
      font-weight:600; font-size:0.9rem; color: var(--fg);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# Focus helper: put a hidden input and an HTML script to focus it automatically
def _keyboard_input_component(key="snake_input", auto_focus_key=0):
    html = f"""
    <div style="position:relative">
      <input id="{key}" type="text" value="" style="opacity:0; width:0; height:0; position: absolute;" />
    </div>
    <script>
      const el = document.getElementById("{key}");
      try {{
        el.focus();
        el.addEventListener('keydown', (e) => {{
          // push keys into streamlit via custom event
          const payload = {{key: e.key}};
          const evt = new CustomEvent("snake_key", {{detail: payload}});
          window.dispatchEvent(evt);
        }});
      }} catch(e) {{}}
      // Focus after interactive events (when auto_focus_key changes)
      window.addEventListener('focus_snake_input_{auto_focus_key}', function() {{
        try {{ el.focus(); }} catch(e) {{}}
      }});
      // Immediately attempt focusing
      setTimeout(()=>{{ try{{ el.focus(); }}catch(e){{}} }}, 120);
    </script>
    """
    st.components.v1.html(html, height=1)

def run_game_loop():
    """
    Non-blocking loop using Streamlit's rerun mechanism.
    The game state is updated, a frame is drawn, and a rerun is triggered.
    """
    ss = st.session_state

    # This is the single-threaded game loop logic
    if ss["running"] and not ss["game_over"]:
        now = now_ms()
        elapsed = now - ss["last_update_ts"]

        if elapsed >= ss["tick_ms"]:
            ss["last_update_ts"] = now
            # handle pending direction change
            ss["direction"] = ss["next_direction"]
            result = step()

            # sound on eat / collision
            if result["ate"] and ss["sound_on"]:
                st.markdown(play_sound_html(ss["eat_sound_b64"]), unsafe_allow_html=True)
            if result["collision"] and ss["game_over"] and ss["sound_on"]:
                st.markdown(play_sound_html(ss["death_sound_b64"]), unsafe_allow_html=True)
            
            # Trigger a rerun to draw the next frame
            if not ss["game_over"]:
                st.rerun()

def main():
    st.set_page_config(page_title="Streamlit Snake", layout="wide", initial_sidebar_state="collapsed")

    init_state()
    _inject_global_css()

    ss = st.session_state

    # Sidebar: settings
    with st.sidebar:
        st.markdown("<h2 style='margin-top:0'>Snake Settings</h2>", unsafe_allow_html=True)
        grid_preset = st.selectbox("Grid size", ("Small 12×12", "Default 20×20", "Large 28×28"),
                                   index=1, disabled=ss["running"])
        if grid_preset == "Small 12×12":
            ss["grid_size"] = (12, 12)
        elif grid_preset == "Large 28×28":
            ss["grid_size"] = (28, 28)
        else:
            ss["grid_size"] = DEFAULT_GRID

        preset_speed = st.select_slider("Speed", options=list(SPEED_PRESETS.keys()),
                                        value="Normal")
        ss["tick_ms"] = SPEED_PRESETS.get(preset_speed, BASE_TICK_MS)

        sound = st.checkbox("Sound effects", value=ss["sound_on"])
        ss["sound_on"] = sound

        st.markdown("---")
        st.markdown("**High score**")
        st.markdown(f"<div class='badge'>{ss.get('high_score', 0)}</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Tips**")
        st.markdown("<div class='meta-label'>Click game area once to focus. Use W/A/S/D. Space = Start/Pause.</div>", unsafe_allow_html=True)

    # Top header and scoreboard
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<h1 style='color:var(--fg); margin-bottom:0.1rem;'>Snake</h1>", unsafe_allow_html=True)
        st.markdown("<div class='meta-label'>Classic snake — WASD + D-pad, responsive, accessible</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div style='text-align:right'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:1.2rem; font-weight:700'>Score: {ss['score']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='meta-label'>Level: {ss['level']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='meta-label'>Streak: {ss['streak']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Layout: main board and controls
    board_col, control_col = st.columns([3, 1], gap="large")

    rows, cols = ss["grid_size"]
    if rows * cols >= (28 * 28):
        ss["cell_size"] = DEFAULT_CELL_MOBILE
    else:
        ss["cell_size"] = DEFAULT_CELL_DESKTOP

    # Board placeholder
    with board_col:
        board_box = st.empty()
        if ss["snake"] is None or ss["food_pos"] is None:
            reset_game()
        img = draw_board(ss["grid_size"], ss["snake"], ss["food_pos"], cell_size=ss["cell_size"], pulse_frame=ss["pulse_frame"])
        board_box.image(img, use_container_width=False)
        
        if ss["game_over"]:
            st.markdown("<div class='snake-toast'>Game Over — Press Play to try again</div>", unsafe_allow_html=True)

    # Controls placeholder (used for audio HTML injection too)
    control_placeholder = control_col.empty()

    # Controls UI (Start/Pause, Restart, D-pad)
    with control_col:
        st.markdown("<h2 style='margin-bottom:0.2rem'>Controls</h2>", unsafe_allow_html=True)
        start_label = "Pause" if ss["running"] else "Start"
        start_paused = st.button(start_label, key="start_pause", help="Space toggles play/pause")
        if start_paused:
            ss["running"] = not ss["running"]
            ss["auto_focus_key"] += 1

        restart_pressed = st.button("Restart", key="restart")
        if restart_pressed:
            reset_game(preserve_high_score=True)
            ss["auto_focus_key"] += 1
            st.rerun()

        st.markdown(f"<div class='meta-label'>Tick: {ss['tick_ms']} ms</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:6px'>Badges:</div>", unsafe_allow_html=True)
        badges_html = " ".join([f"<span class='badge'>{b}</span>" for b in sorted(ss["achievement_badges"])])
        st.markdown(badges_html or "<div class='meta-label'>No badges yet</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        dpad_col1, dpad_col2, dpad_col3 = st.columns([1, 1, 1])
        with dpad_col2:
            if st.button("↑", key="up_btn"):
                handle_direction_input("w")
        with dpad_col1:
            if st.button("←", key="left_btn"):
                handle_direction_input("a")
        with dpad_col3:
            if st.button("→", key="right_btn"):
                handle_direction_input("d")
        with dpad_col2:
            if st.button("↓", key="down_btn"):
                handle_direction_input("s")
        st.markdown("<div class='meta-label' style='margin-top:6px;'>W/A/S/D or use D-pad</div>", unsafe_allow_html=True)

    # Simplified keyboard input using a visible text_input
    typed = st.text_input("Use W/A/S/D to move", value="", key="snake_input_visible", label_visibility="collapsed", help="Click here then use W/A/S/D — hidden", max_chars=1)
    if typed:
        handle_direction_input(typed)
        # We don't need to clear the text input as it's a single character.

    # Start the game loop if running is True
    if ss["running"] and not ss["game_over"]:
        run_game_loop()

    if ss["game_over"]:
        st.markdown("---")
        st.markdown("<h2>Game Over</h2>", unsafe_allow_html=True)
        st.markdown(f"<div>Score: <strong>{ss['score']}</strong></div>", unsafe_allow_html=True)
        st.markdown(f"<div>High score: <strong>{ss['high_score']}</strong></div>", unsafe_allow_html=True)
        if st.button("Play Again"):
            reset_game(preserve_high_score=True)
            ss["auto_focus_key"] += 1
            st.rerun()

    st.markdown("---")
    st.markdown("<div style='display:flex; gap:10px; align-items:center;'>"
                f"<div class='meta-label'>Next level in: {max(0, LEVEL_UP_FOOD - (ss['score'] % LEVEL_UP_FOOD))} foods</div>"
                f"<div style='flex:1'></div>"
                f"<div class='meta-label'>Highscore: {ss['high_score']}</div>"
                "</div>", unsafe_allow_html=True)
    
    # Final persistence of high score
    if ss.get("high_score") is not None:
        try:
            save_high_score(ss["high_score"])
        except Exception:
            pass

if __name__ == "__main__":
    main()