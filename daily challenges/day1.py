import streamlit as st

# Set the page title
st.title("Simple Greeting App")

# Create a form using st.form
with st.form("greeting_form"):
    st.header("Enter Your Details")
    
    # Text input for the name
    name = st.text_input("Your Name")
    
    # Slider for the age
    age = st.slider("Your Age", min_value=1, max_value=120, value=25)
    
    # Form submission button
    submitted = st.form_submit_button("Show Greeting")

# Check if the form was submitted
if submitted:
    if name:
        st.success(f"Hello, {name}! You are {age} years old.")
    else:
        st.warning("Please enter your name to see the greeting.")
