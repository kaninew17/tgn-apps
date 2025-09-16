import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import base64
from PIL import Image

# ================================
# PAGE CONFIGURATION
# ================================
st.set_page_config(
    page_title="Varlam Vaa GYM",
    page_icon="🏋️‍♂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================================
# CUSTOM CSS STYLING
# ================================
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global font styling */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        border-radius: 0 0 20px 20px;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        margin-top: 0.5rem;
        opacity: 0.9;
        font-weight: 400;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    /* Form styling */
    .stForm {
        background: #f8f9ff;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e1e8ed;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Input field styling */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stDateInput label {
        font-size: 1rem !important;
        font-weight: 500 !important;
        color: #2c3e50 !important;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #667eea;
    }
    
    /* Button styling */
    .stFormSubmitButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: transform 0.2s;
    }
    
    .stFormSubmitButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Success message */
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    /* Profile section */
    .profile-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .profile-name {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .profile-details {
        font-size: 1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# EXERCISE DATABASE
# ================================
EXERCISES = [
    "Squat", "Deadlift", "Bench Press", "Overhead Press", "Barbell Row",
    "Pull-ups", "Chin-ups", "Dips", "Push-ups", "Lunges",
    "Bulgarian Split Squat", "Hip Thrust", "Romanian Deadlift", "Incline Bench Press",
    "Decline Bench Press", "Lat Pulldown", "Seated Cable Row", "Leg Press",
    "Leg Curl", "Leg Extension", "Calf Raises", "Bicep Curls", "Tricep Extensions",
    "Lateral Raises", "Front Raises", "Face Pulls", "Shrugs", "Plank",
    "Russian Twists", "Mountain Climbers"
]

FITNESS_GOALS = [
    "Lose Weight", "Build Muscle", "Maintain Fitness", "Increase Strength",
    "Improve Endurance", "Body Recomposition", "Athletic Performance"
]

EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Advanced"]

# ================================
# SESSION STATE INITIALIZATION
# ================================
def initialize_session_state():
    """Initialize all session state variables"""
    if 'workouts' not in st.session_state:
        st.session_state['workouts'] = []
    
    if 'user_profile' not in st.session_state:
        st.session_state['user_profile'] = {
            'name': '',
            'email': '',
            'age': 25,
            'height_cm': 170,
            'weight_kg': 70,
            'gender': 'Male',
            'fitness_goal': 'Build Muscle',
            'experience_level': 'Beginner'
        }

# ================================
# UTILITY FUNCTIONS
# ================================
def get_week_number(date):
    """Get ISO week number for a given date"""
    return date.isocalendar()[1]

def get_year_week(date):
    """Get year-week string for grouping"""
    year, week, _ = date.isocalendar()
    return f"{year}-W{week:02d}"

def calculate_volume(sets, reps, weight):
    """Calculate workout volume (Sets × Reps × Weight)"""
    return sets * reps * weight

def kg_to_lbs(kg):
    """Convert kg to lbs"""
    return kg * 2.20462

def lbs_to_kg(lbs):
    """Convert lbs to kg"""
    return lbs / 2.20462

# ================================
# MAIN APPLICATION
# ================================
def main():
    initialize_session_state()
    
    # App Header
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🏋️‍♂️ Varlam Vaa GYM</h1>
        <p class="main-subtitle">Your Personal Workout Logger & Progress Tracker</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User Profile Section
    show_user_profile()
    
    # Workout Input Form
    show_workout_form()
    
    # Display workout data if available
    if st.session_state['workouts']:
        show_workout_history()
        show_weekly_volume_chart()
        show_personal_records()
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #6c757d;">
            <h3>🎯 Ready to start your fitness journey?</h3>
            <p>Log your first workout above to see your progress charts and personal records!</p>
        </div>
        """, unsafe_allow_html=True)

def show_user_profile():
    """Display and manage user profile"""
    st.markdown('<h2 class="section-header">👤 User Profile</h2>', unsafe_allow_html=True)
    
    with st.expander("Edit Profile", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", value=st.session_state['user_profile']['name'])
            email = st.text_input("Email Address", value=st.session_state['user_profile']['email'])
            age = st.number_input("Age", min_value=13, max_value=100, 
                                value=st.session_state['user_profile']['age'])
            height_cm = st.number_input("Height (cm)", min_value=100, max_value=250,
                                      value=st.session_state['user_profile']['height_cm'])
        
        with col2:
            weight_kg = st.number_input("Weight (kg)", min_value=30, max_value=300,
                                      value=st.session_state['user_profile']['weight_kg'])
            gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                                index=["Male", "Female", "Other"].index(st.session_state['user_profile']['gender']))
            fitness_goal = st.selectbox("Fitness Goal", FITNESS_GOALS,
                                      index=FITNESS_GOALS.index(st.session_state['user_profile']['fitness_goal']))
            experience_level = st.selectbox("Experience Level", EXPERIENCE_LEVELS,
                                          index=EXPERIENCE_LEVELS.index(st.session_state['user_profile']['experience_level']))
        
        if st.button("Update Profile", key="update_profile"):
            st.session_state['user_profile'].update({
                'name': name,
                'email': email,
                'age': age,
                'height_cm': height_cm,
                'weight_kg': weight_kg,
                'gender': gender,
                'fitness_goal': fitness_goal,
                'experience_level': experience_level
            })
            st.success("✅ Profile updated successfully!")
    
    # Display current profile
    if st.session_state['user_profile']['name']:
        profile = st.session_state['user_profile']
        st.markdown(f"""
        <div class="profile-section">
            <div class="profile-name">👋 Welcome back, {profile['name']}!</div>
            <div class="profile-details">
                📧 {profile['email']} | 🎂 {profile['age']} years old | 📏 {profile['height_cm']} cm | ⚖️ {profile['weight_kg']} kg<br>
                🎯 Goal: {profile['fitness_goal']} | 💪 Level: {profile['experience_level']}
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_workout_form():
    """Display workout input form"""
    st.markdown('<h2 class="section-header">📝 Log New Workout</h2>', unsafe_allow_html=True)
    
    with st.form("workout_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            workout_date = st.date_input("Date", value=datetime.now().date())
            exercise_name = st.selectbox("Exercise", EXERCISES)
            sets = st.number_input("Sets", min_value=1, max_value=20, value=3)
        
        with col2:
            reps = st.number_input("Reps", min_value=1, max_value=100, value=10)
            weight = st.number_input("Weight", min_value=0.0, step=0.5, value=50.0)
            unit = st.selectbox("Unit", ["kg", "lbs"])
        
        # Form submit button
        submitted = st.form_submit_button("🚀 Log Workout")
        
        if submitted:
            # Convert weight to kg for consistent storage
            weight_kg = weight if unit == "kg" else lbs_to_kg(weight)
            
            # Calculate volume
            volume = calculate_volume(sets, reps, weight_kg)
            
            # Create workout entry
            workout_entry = {
                'date': workout_date,
                'exercise': exercise_name,
                'sets': sets,
                'reps': reps,
                'weight_kg': weight_kg,
                'weight_display': weight,
                'unit': unit,
                'volume_kg': volume,
                'timestamp': datetime.now()
            }
            
            # Add to session state
            st.session_state['workouts'].append(workout_entry)
            
            # Success message
            st.markdown(f"""
            <div class="success-message">
                <strong>🎉 Workout Logged Successfully!</strong><br>
                {exercise_name}: {sets} sets × {reps} reps @ {weight} {unit}
                (Volume: {volume:.1f} kg)
            </div>
            """, unsafe_allow_html=True)
            
            st.rerun()

def show_workout_history():
    """Display workout history table"""
    st.markdown('<h2 class="section-header">📊 Workout History</h2>', unsafe_allow_html=True)
    
    # Create DataFrame
    df = pd.DataFrame(st.session_state['workouts'])
    df_display = df.copy()
    
    # Convert date column to datetime if it isn't already
    df_display['date'] = pd.to_datetime(df_display['date'])
    df['date'] = pd.to_datetime(df['date'])
    
    # Format for display
    df_display['Date'] = df_display['date'].dt.strftime('%Y-%m-%d')
    df_display['Exercise'] = df_display['exercise']
    df_display['Sets'] = df_display['sets']
    df_display['Reps'] = df_display['reps']
    df_display['Weight'] = df_display.apply(lambda row: f"{row['weight_display']:.1f} {row['unit']}", axis=1)
    df_display['Volume (kg)'] = df_display['volume_kg'].round(1)
    
    # Select and sort
    display_columns = ['Date', 'Exercise', 'Sets', 'Reps', 'Weight', 'Volume (kg)']
    df_display = df_display[display_columns].sort_values('Date', ascending=False)
    
    # Display table
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Workouts", len(df))
    
    with col2:
        total_volume = df['volume_kg'].sum()
        st.metric("Total Volume (kg)", f"{total_volume:,.0f}")
    
    with col3:
        unique_exercises = df['exercise'].nunique()
        st.metric("Unique Exercises", unique_exercises)
    
    with col4:
        if len(df) > 0:
            days_active = (df['date'].max() - df['date'].min()).days + 1
            st.metric("Days Active", days_active)

def show_weekly_volume_chart():
    """Display weekly volume progression chart"""
    st.markdown('<h2 class="section-header">📈 Weekly Volume Progression</h2>', unsafe_allow_html=True)
    
    df = pd.DataFrame(st.session_state['workouts'])
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Exercise filter
    exercises = ["All Exercises"] + sorted(df['exercise'].unique().tolist())
    selected_exercise = st.selectbox("Select Exercise", exercises, key="exercise_filter")
    
    # Filter data
    if selected_exercise != "All Exercises":
        df_filtered = df[df['exercise'] == selected_exercise]
    else:
        df_filtered = df
    
    if len(df_filtered) > 0:
        # Group by week
        df_filtered['year_week'] = df_filtered['date'].apply(get_year_week)
        weekly_volume = df_filtered.groupby('year_week')['volume_kg'].sum().reset_index()
        weekly_volume.columns = ['Week', 'Total Volume (kg)']
        
        # Create chart
        st.line_chart(data=weekly_volume.set_index('Week'), y='Total Volume (kg)')
        
        # Display weekly stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_weekly = weekly_volume['Total Volume (kg)'].mean()
            st.metric("Avg Weekly Volume", f"{avg_weekly:.0f} kg")
        
        with col2:
            max_weekly = weekly_volume['Total Volume (kg)'].max()
            st.metric("Best Week", f"{max_weekly:.0f} kg")
        
        with col3:
            if len(weekly_volume) >= 2:
                recent_trend = weekly_volume['Total Volume (kg)'].iloc[-1] - weekly_volume['Total Volume (kg)'].iloc[-2]
                st.metric("Weekly Change", f"{recent_trend:+.0f} kg", delta=f"{recent_trend:+.0f}")
    
    else:
        st.info("No data available for the selected exercise.")

def show_personal_records():
    """Display personal records for each exercise"""
    st.markdown('<h2 class="section-header">🏆 Personal Records</h2>', unsafe_allow_html=True)
    
    df = pd.DataFrame(st.session_state['workouts'])
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate PRs for each exercise
    prs = df.groupby('exercise').agg({
        'weight_kg': 'max',
        'weight_display': 'first',
        'unit': 'first',
        'date': 'last'
    }).reset_index()
    
    # Sort by weight descending
    prs = prs.sort_values('weight_kg', ascending=False)
    
    # Display PRs in a grid
    if len(prs) > 0:
        # Create columns for responsive grid
        cols_per_row = 3
        rows = (len(prs) + cols_per_row - 1) // cols_per_row
        
        for row in range(rows):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                pr_idx = row * cols_per_row + col_idx
                if pr_idx < len(prs):
                    pr = prs.iloc[pr_idx]
                    
                    # Find the actual weight used for this PR
                    pr_workout = df[(df['exercise'] == pr['exercise']) & 
                                   (df['weight_kg'] == pr['weight_kg'])].iloc[-1]
                    
                    weight_display = f"{pr_workout['weight_display']:.1f} {pr_workout['unit']}"
                    
                    with cols[col_idx]:
                        st.metric(
                            label=f"🏋️‍♂️ {pr['exercise']}",
                            value=weight_display,
                            help=f"Set on {pr['date'].strftime('%Y-%m-%d')}"
                        )
    
    else:
        st.info("Complete some workouts to see your personal records!")

if __name__ == "__main__":
    main()