import streamlit as st

def calculate(num1, num2, operation):
    """
    Performs a mathematical operation on two numbers.

    Args:
        num1 (float): The first number.
        num2 (float): The second number.
        operation (str): The operation to perform ('+', '-', '*', '/').

    Returns:
        float or str: The result of the operation or an error message.
    """
    if operation == '+':
        return num1 + num2
    elif operation == '-':
        return num1 - num2
    elif operation == '*':
        return num1 * num2
    elif operation == '/':
        # Handle division by zero
        if num2 == 0:
            return "error"
        return num1 / num2
    return "error" # Should not be reached with the given options

# --- UI Layout and Widgets ---
st.set_page_config(page_title="Simple Calculator", layout="centered")

st.title("Simple Calculator ➕➖✖️➗")

# Use a form to group inputs and the button, preventing re-execution
with st.form(key='calculator_form'):
    
    # Input widgets for the two numbers
    col1, col2 = st.columns(2)
    with col1:
        num1 = st.number_input(
            label="First Number",
            value=0.0,
            format="%g"
        )
    with col2:
        num2 = st.number_input(
            label="Second Number",
            value=0.0,
            format="%g"
        )
    
    # Operation selector
    operation = st.selectbox(
        label="Select Operation",
        options=('+', '-', '*', '/')
    )
    
    # Calculate button inside the form
    calculate_button = st.form_submit_button(label='➔ Calculate')

# --- Logic and Result Display ---
if calculate_button:
    result = calculate(num1, num2, operation)
    
    # Division by zero error handling
    if result == "error":
        st.error("Cannot divide by zero!")
    else:
        # Custom result display
        st.success(f"Result: {num1} {operation} {num2} = {result}")