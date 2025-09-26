import streamlit as st
import time

# Page configuration
st.set_page_config(
    page_title="Simple Stopwatch",
    page_icon="⏱️",
    layout="centered"
)

# Custom CSS with better visibility
st.markdown("""
<style>
    .timer-display {
        font-size: 72px;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
        font-family: monospace;
        background: #000000;
        color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        border: 3px solid #333;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    .status-chip {
        display: inline-block;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: 600;
        margin: 15px 0;
        font-size: 18px;
    }
    .status-running { background: #10b981; color: white; }
    .status-paused { background: #f59e0b; color: white; }
    .status-idle { background: #6b7280; color: white; }
    
    /* Button styling */
    .stButton > button {
        font-size: 18px;
        font-weight: 600;
        padding: 15px 25px;
        border-radius: 10px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* Lap list styling */
    .lap-item {
        background: #f8f9fa;
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 4px solid #6366f1;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize all session state variables"""
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'elapsed_time' not in st.session_state:
        st.session_state.elapsed_time = 0.0
    if 'last_update' not in st.session_state:
        st.session_state.last_update = 0

def format_time(seconds):
    """Format seconds to MM:SS.mmm"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"

def get_current_time():
    """Get current elapsed time in seconds"""
    if st.session_state.running and st.session_state.start_time:
        current_elapsed = time.time() - st.session_state.start_time
        return st.session_state.elapsed_time + current_elapsed
    return st.session_state.elapsed_time

def start_stopwatch():
    """Start the stopwatch"""
    if not st.session_state.running:
        st.session_state.running = True
        st.session_state.start_time = time.time()

def stop_stopwatch():
    """Stop the stopwatch"""
    if st.session_state.running:
        st.session_state.elapsed_time = get_current_time()
        st.session_state.running = False
        st.session_state.start_time = None

def reset_stopwatch():
    """Reset the stopwatch"""
    st.session_state.running = False
    st.session_state.start_time = None
    st.session_state.elapsed_time = 0.0
    if 'laps' in st.session_state:
        st.session_state.laps = []

def main():
    # Initialize session state
    init_session_state()
    
    st.title("⏱️ Simple Stopwatch")
    
    # Get current time
    current_time = get_current_time()
    
    # Display status
    if st.session_state.running:
        status = "RUNNING"
        status_class = "status-running"
    elif current_time > 0:
        status = "PAUSED"
        status_class = "status-paused"
    else:
        status = "READY"
        status_class = "status-idle"
    
    st.markdown(f'<div style="text-align: center;"><div class="status-chip {status_class}">{status}</div></div>', unsafe_allow_html=True)
    
    # Display timer - using a placeholder for dynamic updates
    timer_placeholder = st.empty()
    with timer_placeholder.container():
        st.markdown(f'<div class="timer-display">{format_time(current_time)}</div>', unsafe_allow_html=True)
    
    # Control buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.running:
            if st.button("⏸️ Stop", use_container_width=True, key="stop_btn"):
                stop_stopwatch()
                st.rerun()
        else:
            if st.button("▶️ Start", use_container_width=True, key="start_btn"):
                start_stopwatch()
                st.rerun()
    
    with col2:
        if st.button("🔄 Reset", use_container_width=True, key="reset_btn"):
            reset_stopwatch()
            st.rerun()
    
    with col3:
        if st.button("📍 Lap", use_container_width=True, disabled=not st.session_state.running, key="lap_btn"):
            if 'laps' not in st.session_state:
                st.session_state.laps = []
            st.session_state.laps.append(current_time)
            st.rerun()
    
    # Display lap count if any
    if 'laps' in st.session_state and st.session_state.laps:
        lap_count = len(st.session_state.laps)
        st.subheader(f"Lap Count: {lap_count}")
        st.markdown(f'<div class="lap-item"><strong>Total Laps Completed:</strong> {lap_count}</div>', unsafe_allow_html=True)
    
    # Auto-refresh when running
    if st.session_state.running:
        time.sleep(0.01)  # Small delay
        st.rerun()

if __name__ == "__main__":
    main()