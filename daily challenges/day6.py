import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta, time

# --- Page Configuration ---
st.set_page_config(
    page_title="Daily Water Intake Tracker",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constants & File Path ---
DATA_FILE = "water_data.csv"
BODY_SVG_PATH = "https://raw.githubusercontent.com/artofdata-bq/streamlit-apps/main/water_tracker/body.svg" # Simple body SVG

# --- Data Handling Functions ---

@st.cache_data
def load_data():
    """Loads water intake data from a CSV file."""
    try:
        df = pd.read_csv(DATA_FILE)
        # Ensure date columns are in datetime format
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    except FileNotFoundError:
        # Create an empty DataFrame if the file doesn't exist
        df = pd.DataFrame(columns=['Date', 'Timestamp', 'Amount_ml', 'Daily_Goal_ml'])
    return df

def save_data(df):
    """Saves the DataFrame to the CSV file."""
    df.to_csv(DATA_FILE, index=False)
    # Bust the cache for load_data
    st.cache_data.clear()

def add_entry(df, entry_date, amount_ml, goal_ml):
    """Adds a new water intake entry to the DataFrame."""
    new_entry = pd.DataFrame([{
        'Date': entry_date,
        'Timestamp': datetime.now(),
        'Amount_ml': amount_ml,
        'Daily_Goal_ml': goal_ml
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    return df

# --- Visualization Functions ---

def get_color_and_level(intake_ml):
    """Determines the color and hydration level based on intake."""
    if intake_ml < 1500:
        return "#FF4B4B", "Critical" # Red
    elif 1500 <= intake_ml < 2500:
        return "#FFD700", "Good" # Orange/Gold
    elif 2500 <= intake_ml < 2900:
        return "#1E90FF", "Great" # Blue
    else:
        return "#32CD32", "Goal Achieved!" # Green

def create_body_svg(intake_ml, goal_ml):
    """Generates an SVG of a human body that fills with water."""
    percentage = min(100, (intake_ml / goal_ml) * 100) if goal_ml > 0 else 0
    fill_color, _ = get_color_and_level(intake_ml)
    
    # Simple human body silhouette SVG path
    svg_body = f"""
    <svg width="150" height="350" viewBox="0 0 200 450" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="waterFill" x1="0%" y1="100%" x2="0%" y2="0%">
          <stop offset="0%" style="stop-color:{fill_color};stop-opacity:1" />
          <stop offset="{percentage}%" style="stop-color:{fill_color};stop-opacity:1" />
          <stop offset="{percentage}%" style="stop-color:#E0E0E0;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#E0E0E0;stop-opacity:1" />
        </linearGradient>
      </defs>
      <path d="M100 5C72.3858 5 50 27.3858 50 55C50 82.6142 72.3858 105 100 105C127.614 105 150 82.6142 150 55C150 27.3858 127.614 5 100 5Z" fill="url(#waterFill)" stroke="#333" stroke-width="4"/>
      <path d="M100 110C60 110 30 140 30 180V350C30 380 50 400 70 400H80V440H120V400H130C150 400 170 380 170 350V180C170 140 140 110 100 110Z" fill="url(#waterFill)" stroke="#333" stroke-width="4"/>
    </svg>
    """
    return svg_body

# --- App Layout & Logic ---

# Load data initially
water_df = load_data()

# --- Sidebar ---
with st.sidebar:
    st.header("💧 Hydration Hub")
    st.markdown("---")
    
    # 1. User Onboarding: Goal Setting
    st.subheader("Set Your Daily Goal")
    daily_goal_ml = st.number_input(
        "Daily water intake goal (ml)", 
        min_value=1000, 
        max_value=7000, 
        value=st.session_state.get('daily_goal', 3000), 
        step=100
    )
    if st.button("Set Goal", use_container_width=True):
        st.session_state.daily_goal = daily_goal_ml
        st.success(f"Goal set to {daily_goal_ml} ml!")
        
    # Check if goal is set to proceed
    if 'daily_goal' not in st.session_state:
        st.info("Please set your goal to start tracking.")
        st.stop()
        
    st.markdown("---")

    # 4. Hydration Education
    with st.expander("💧 The Importance of Hydration & Tips"):
        st.markdown("""
        **Key Benefits of Staying Hydrated:**
        - **Maximizes Physical Performance:** Dehydration can lead to reduced endurance and strength.
        - **Improves Brain Function:** Proper hydration is key for concentration, cognition, and mood.
        - **Regulates Body Temperature:** Water helps dissipate heat from your body.
        - **Prevents Headaches:** Dehydration is a common trigger for headaches and migraines.
        - **Supports Digestive Health:** Water helps break down food and prevent constipation.

        **Tips for Proper Hydration:**
        - Always keep a water bottle on your desk or with you.
        - Infuse water with fruits like lemon, cucumber, or berries for flavor.
        - Drink a glass of water before every meal.
        - Set reminders on your phone or use this app daily!
        - Eat water-rich foods like watermelon, strawberries, and celery.
        """)

# --- Main App Area ---
st.title("Daily Water Intake Tracker")

# Date & Time Context
selected_date = st.date_input("Select Entry Date", date.today())

# Filter data for the selected day and calculate total
today_df = water_df[water_df['Date'] == selected_date]
total_intake_today = today_df['Amount_ml'].sum()

# --- Main Columns: Progress Visual & Input ---
col1, col2 = st.columns([0.6, 0.4], gap="large")

# --- Column 1: Progress Visualization ---
with col1:
    st.header("Today's Progress")
    
    # 2. Numerical Progress
    color, level = get_color_and_level(total_intake_today)
    st.metric(
        label="Current Intake",
        value=f"{total_intake_today / 1000:.2f} L",
        delta=f"Goal: {st.session_state.daily_goal / 1000:.2f} L"
    )

    # 2. Visual Goal Tracker
    st.markdown(f"<p style='color:{color}; font-weight:bold; text-align:center;'>Hydration Level: {level}</p>", unsafe_allow_html=True)
    body_svg = create_body_svg(total_intake_today, st.session_state.daily_goal)
    st.markdown(f"<div style='display: flex; justify-content: center;'>{body_svg}</div>", unsafe_allow_html=True)


# --- Column 2: Logging Inputs ---
with col2:
    st.header("Log Your Intake")
    
    # 1. Water Input Mechanism
    # Using number_input is more flexible than a slider for various units
    amount_input = st.number_input("Log amount", min_value=0, step=50, value=250)
    unit_selection = st.radio("Unit", ["ml", "L"], horizontal=True)

    # Convert input to ml
    amount_ml_to_add = int(amount_input * 1000) if unit_selection == 'L' else int(amount_input)

    # Submit button for the primary input
    if st.button(f"Add {amount_ml_to_add} ml", use_container_width=True):
        if amount_ml_to_add > 0:
            water_df = add_entry(water_df, selected_date, amount_ml_to_add, st.session_state.daily_goal)
            save_data(water_df)
            st.success(f"✅ Added {amount_ml_to_add} ml!")
            st.rerun()

    st.markdown("<hr style='margin-top: 2rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
    
    # Quick Add Buttons
    st.subheader("Quick Add")
    quick_add_cols = st.columns(3)
    quick_add_values = [250, 500, 750] # ml
    
    for i, val in enumerate(quick_add_values):
        if quick_add_cols[i].button(f"{val} ml", use_container_width=True, key=f"quick_{val}"):
            water_df = add_entry(water_df, selected_date, val, st.session_state.daily_goal)
            save_data(water_df)
            st.success(f"✅ Added {val} ml!")
            st.rerun()

# --- Data History & Charts ---
st.markdown("---")

with st.expander("📊 Weekly Progress Overview", expanded=True):
    # 3. Weekly Hydration Chart
    # Determine the start (Sunday) and end (Saturday) of the week for the selected date
    start_of_week = selected_date - timedelta(days=(selected_date.weekday() + 1) % 7)
    end_of_week = start_of_week + timedelta(days=6)
    
    # Filter data for the full week
    weekly_df = water_df[
        (water_df['Date'] >= start_of_week) & 
        (water_df['Date'] <= end_of_week)
    ]
    
    # Group by date and sum intake, then convert to Liters
    daily_summary = weekly_df.groupby('Date')['Amount_ml'].sum().reset_index()
    daily_summary['Amount_L'] = daily_summary['Amount_ml'] / 1000
    
    # Create a full date range for the week to show days with zero intake
    week_date_range = pd.date_range(start=start_of_week, end=end_of_week).to_frame(index=False, name='Date')
    week_date_range['Date'] = week_date_range['Date'].dt.date
    
    # Merge with actual data
    merged_summary = pd.merge(week_date_range, daily_summary, on='Date', how='left').fillna(0)
    merged_summary['Day'] = pd.to_datetime(merged_summary['Date']).dt.strftime('%A')
    
    # Create Plotly Chart
    fig = px.bar(
        merged_summary,
        x='Day',
        y='Amount_L',
        title=f"Weekly Intake ({start_of_week.strftime('%d %b')} - {end_of_week.strftime('%d %b')})",
        labels={'Amount_L': 'Total Water Intake (L)', 'Day': ''},
        text='Amount_L'
    )
    
    # Add goal line
    fig.add_hline(
        y=st.session_state.daily_goal / 1000,
        line_dash="dash",
        line_color="green",
        annotation_text="Daily Goal",
        annotation_position="bottom right"
    )
    
    fig.update_traces(texttemplate='%{text:.2f} L', textposition='outside', marker_color='#1E90FF')
    fig.update_layout(
        uniformtext_minsize=8, 
        uniformtext_mode='hide',
        yaxis_title="Total Intake (L)",
        xaxis={'categoryorder':'array', 'categoryarray': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']}
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Show raw data in a toggleable table
    if st.checkbox("Show Raw Log Data for Selected Day"):
        st.dataframe(
            today_df[['Timestamp', 'Amount_ml']].rename(columns={'Timestamp': 'Log Time', 'Amount_ml': 'Amount (ml)'}),
            use_container_width=True,
            hide_index=True
        )