import streamlit as st 
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Event Registration System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling and increased font sizes
st.markdown("""
<style>
    html, body, [class*="st-"] {
        font-size: 18px !important; /* Base font size, now with !important */
    }
    
    h1 {
        font-size: 3rem !important;
    }
    
    h2 {
        font-size: 2.5rem !important;
    }
    
    h3 {
        font-size: 2rem !important;
    }
    
    p {
        font-size: 1.2rem !important;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        font-size: 3.5rem !important;
    }
    
    .main-header p {
        font-size: 1.8rem !important;
    }
    
    .event-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border-left: 5px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .event-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .event-title {
        color: #2c3e50;
        font-size: 2.2rem !important;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .event-details {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .event-details p {
        font-size: 1.2rem !important;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .registration-form {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .success-message {
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
    }
    
    .admin-header {
        background: linear-gradient(135deg, #2d3436, #636e72);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        font-size: 1.2rem !important;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .sidebar .stButton > button {
        font-size: 1.1rem !important;
    }
    
    .event-image {
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease;
    }
    
    .event-image:hover {
        transform: scale(1.05);
    }
    
    .stMarkdown, .stMetric, .stDataFrame, .stExpander, .stDownloadButton, .stTextInput, .stNumberInput {
        font-size: 1.2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'registrations' not in st.session_state:
    st.session_state.registrations = []

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

if 'selected_event' not in st.session_state:
    st.session_state.selected_event = None

# Event data with random movie/event thumbnails
EVENTS = [
    {
        'title': 'Lokah Chapter 1: Chandra',
        'description': 'An epic tale of mystery and adventure that will keep you on the edge of your seat.',
        'image_url': 'https://images.unsplash.com/photo-1489599037986-d6b75d9b34e8?w=400&h=600&fit=crop&crop=faces',
        'link': 'https://in.bookmyshow.com/movies/chennai/lokah-chapter-1-chandra/ET00456016',
        'date': '31.09.2025',
        'time': '9:00 PM',
        'venue': 'Marina Mall',
        'full_description': 'Come let\'s enjoy the movie together.'
    },
    {
        'title': 'Madharaasi',
        'description': 'A gripping drama that explores the depths of human emotions and relationships.',
        'image_url': 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=400&h=600&fit=crop&crop=faces',
        'link': 'https://in.bookmyshow.com/movies/chennai/madharaasi/ET00434543',
        'date': '31.09.2025',
        'time': '9:00 PM',
        'venue': 'Marina Mall',
        'full_description': 'Come let\'s enjoy the movie together.'
    },
    {
        'title': 'Thandakaaranyam',
        'description': 'A thrilling journey through uncharted territories of storytelling.',
        'image_url': 'https://images.unsplash.com/photo-1518676590629-3dcbd9c5a5c9?w=400&h=600&fit=crop&crop=center',
        'link': 'https://in.bookmyshow.com/movies/chennai/thandakaaranyam/ET00445048',
        'date': '31.09.2025',
        'time': '9:00 PM',
        'venue': 'Marina Mall',
        'full_description': 'Come let\'s enjoy the movie together.'
    },
    {
        'title': 'Ajey: The Untold Story of a Yogi',
        'description': 'An inspiring biographical tale of spiritual awakening and self-discovery.',
        'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=600&fit=crop&crop=center',
        'link': 'https://in.bookmyshow.com/movies/chennai/ajey-the-untold-story-of-a-yogi/ET00450678',
        'date': '31.09.2025',
        'time': '9:00 PM',
        'venue': 'Marina Mall',
        'full_description': 'Come let\'s enjoy the movie together.'
    }
]

def get_total_registrations():
    """Calculate total number of registrations"""
    return sum([reg['tickets'] for reg in st.session_state.registrations])

def get_total_registrants():
    """Calculate total number of registrants"""
    return len(st.session_state.registrations)

def export_registrations_csv():
    """Export registrations to CSV"""
    if st.session_state.registrations:
        df = pd.DataFrame(st.session_state.registrations)
        return df.to_csv(index=False)
    return ""

def display_event_image(image_url, alt_text="Event Image"):
    """Display event image with fallback"""
    try:
        st.markdown(f'<img src="{image_url}" class="event-image" style="width: 100%; max-width: 300px; height: 400px; object-fit: cover;" alt="{alt_text}">', unsafe_allow_html=True)
    except:
        # Fallback to a placeholder if image fails to load
        st.markdown(f"""
        <div style="width: 100%; max-width: 300px; height: 400px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
             display: flex; align-items: center; justify-content: center; border-radius: 10px; color: white; font-size: 18px; text-align: center;">
            🎬<br>{alt_text}
        </div>
        """, unsafe_allow_html=True)

def show_home_page():
    """Display the home page with events"""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎬 Event Registration System</h1>
        <p>Discover and register for amazing events</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Events listing
    st.markdown("## 🎭 Available Events")
    
    for i, event in enumerate(EVENTS):
        with st.container():
            col1, col2 = st.columns([1, 2])
            
            with col1:
                display_event_image(event['image_url'], event['title'])
            
            with col2:
                st.markdown(f'<div class="event-title">{event["title"]}</div>', unsafe_allow_html=True)
                st.write(event['description'])
                
                # Event details in a styled container
                st.markdown('<div class="event-details">', unsafe_allow_html=True)
                st.write(f"**📅 Date:** {event['date']}")
                st.write(f"**🕘 Time:** {event['time']}")
                st.write(f"**📍 Venue:** {event['venue']}")
                st.write(f"**📝 Description:** {event['full_description']}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Add some spacing and styling
                st.markdown("---")
                
                # Use columns for better button layout
                col_btn, col_link = st.columns([1, 1])
                with col_btn:
                    if st.button(f"🎫 Register Now", key=f"register_{i}", type="primary"):
                        st.session_state.selected_event = event
                        st.session_state.current_page = 'register'
                        st.rerun()
                
                with col_link:
                    st.markdown(f"[🔗 View on BookMyShow]({event['link']})", unsafe_allow_html=True)
        
        st.markdown("---")

def show_registration_page():
    """Display the registration form"""
    if st.session_state.selected_event is None:
        st.error("No event selected!")
        if st.button("← Back to Home"):
            st.session_state.current_page = 'home'
            st.rerun()
        return
    
    event = st.session_state.selected_event
    
    # Back button
    if st.button("← Back to Events"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown(f"""
    <div class="main-header">
        <h1>📝 Register for Event</h1>
        <h2>{event['title']}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Event details recap
    col1, col2 = st.columns([1, 2])
    with col1:
        display_event_image(event['image_url'], event['title'])
    
    with col2:
        st.markdown(f'<h3 style="color: #2c3e50; margin-bottom: 1rem;">Event Details</h3>', unsafe_allow_html=True)
        st.markdown('<div class="event-details">', unsafe_allow_html=True)
        st.write(f"**📅 Date:** {event['date']}")
        st.write(f"**🕘 Time:** {event['time']}")
        st.write(f"**📍 Venue:** {event['venue']}")
        st.write(f"**📝 Description:** {event['full_description']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Registration form
    with st.container():
        st.markdown('<div class="registration-form">', unsafe_allow_html=True)
        st.markdown("### Registration Information")
        
        with st.form("registration_form"):
            name = st.text_input("Full Name *", placeholder="Enter your full name")
            email = st.text_input("Email Address *", placeholder="Enter your email address")
            tickets = st.number_input("Number of Tickets *", min_value=1, max_value=10, value=1)
            
            submitted = st.form_submit_button("🎫 Complete Registration")
            
        if submitted:
            if name and email and tickets:
                # Save registration
                registration = {
                    'name': name,
                    'email': email,
                    'tickets': tickets,
                    'event': event['title'],
                    'registration_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.registrations.append(registration)
                
                st.markdown("""
                <div class="success-message">
                    <h3>🎉 Successfully registered!</h3>
                    <p>Thank you for registering. We look forward to seeing you at the event!</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show registration summary
                st.markdown("### Registration Summary")
                st.write(f"**Name:** {name}")
                st.write(f"**Email:** {email}")
                st.write(f"**Event:** {event['title']}")
                st.write(f"**Tickets:** {tickets}")
                st.write(f"**Registration Time:** {registration['registration_time']}")
                
                # if st.button("Register for Another Event"):
                #     st.session_state.current_page = 'home'
                #     st.session_state.selected_event = None
                #     st.rerun()
            else:
                st.error("Please fill in all required fields!")
        
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Register for Another Event"):
        st.session_state.current_page = 'home'
        st.session_state.selected_event = None
        st.rerun()

def show_admin_panel():
    """Display the admin panel"""
    st.markdown("""
    <div class="admin-header">
        <h1>👨‍💼 Admin Panel</h1>
        <p>Manage events and view registration logs</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different admin sections
    tab1, tab2 = st.tabs(["📊 Registration Analytics", "📋 Registration Logs"])
    
    with tab1:
        st.markdown("### Registration Statistics")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Events", len(EVENTS))
        with col2:
            st.metric("Total Registrants", get_total_registrants())
        with col3:
            st.metric("Total Tickets", get_total_registrations())
        with col4:
            avg_tickets = get_total_registrations() / max(get_total_registrants(), 1)
            st.metric("Avg Tickets/Person", f"{avg_tickets:.1f}")
        
        st.markdown("---")
        
        # Event-wise registration count
        if st.session_state.registrations:
            event_stats = {}
            for reg in st.session_state.registrations:
                event = reg['event']
                if event not in event_stats:
                    event_stats[event] = {'registrants': 0, 'tickets': 0}
                event_stats[event]['registrants'] += 1
                event_stats[event]['tickets'] += reg['tickets']
            
            st.markdown("### Event-wise Registration Summary")
            for event, stats in event_stats.items():
                st.write(f"**{event}:** {stats['registrants']} registrants, {stats['tickets']} tickets")
        else:
            st.info("No registrations yet.")
    
    with tab2:
        st.markdown("### Registration Logs")
        
        if st.session_state.registrations:
            # Convert to DataFrame for better display
            df = pd.DataFrame(st.session_state.registrations)
            
            # Display the registration table
            st.dataframe(
                df[['name', 'email', 'event', 'tickets', 'registration_time']],
                column_config={
                    'name': 'Name',
                    'email': 'Email',
                    'event': 'Event',
                    'tickets': 'Tickets',
                    'registration_time': 'Registration Time'
                },
                use_container_width=True
            )
            
            st.markdown("---")
            
            # Export functionality
            csv_data = export_registrations_csv()
            if csv_data:
                st.download_button(
                    label="📥 Download Registration Data (CSV)",
                    data=csv_data,
                    file_name=f"event_registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No registrations to display yet.")

def show_events_list():
    """Display the events list for admin"""
    st.markdown("""
    <div class="admin-header">
        <h1>📋 Events List</h1>
        <p>Currently available events</p>
    </div>
    """, unsafe_allow_html=True)
    
    for i, event in enumerate(EVENTS, 1):
        with st.expander(f"{i}. {event['title']}"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                display_event_image(event['image_url'], event['title'])
            
            with col2:
                st.write(f"**Description:** {event['description']}")
                st.write(f"**Date:** {event['date']}")
                st.write(f"**Time:** {event['time']}")
                st.write(f"**Venue:** {event['venue']}")
                st.write(f"**Full Description:** {event['full_description']}")
                st.write(f"**BookMyShow Link:** [View Details]({event['link']})")

# Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 1rem;">
        <h2>🎬 Navigation</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()
    
    if st.button("📋 List of Events", use_container_width=True):
        st.session_state.current_page = 'events_list'
        st.rerun()
    
    if st.button("👨‍💼 Admin Panel", use_container_width=True):
        st.session_state.current_page = 'admin'
        st.rerun()
    
    st.markdown("")

# Main content area
if st.session_state.current_page == 'home':
    show_home_page()
elif st.session_state.current_page == 'register':
    show_registration_page()
elif st.session_state.current_page == 'admin':
    show_admin_panel()
elif st.session_state.current_page == 'events_list':
    show_events_list()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem; color: #666;">
    <p>🎬 Event Registration System | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
