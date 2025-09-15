import streamlit as st
import requests
from datetime import datetime
from typing import Dict, Tuple, Optional

# Page configuration for mobile-friendly layout
st.set_page_config(
    page_title="Instant Unit Converter",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile responsiveness, accessibility, and styling
st.markdown("""
    <style>
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .stNumberInput, .stSelectbox, .stButton {
            width: 100% !important;
        }
        div[data-testid="column"] {
            width: 100% !important;
            padding: 0.5rem;
        }
    }
    
    /* Main styling */
    .main-title {
        font-size: 1.8rem;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    
    .conversion-section {
        background-color: #f8f9fa;
        padding: 1.2rem;
        border-radius: 0.8rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid #2e86c1;
    }
    
    .result-box {
        background-color: #fff9c4;
        padding: 1.2rem;
        border-radius: 0.8rem;
        margin-top: 1rem;
        border: 1px solid #ffd600;
    }
    
    .result-text {
        font-size: 1.4rem;
        font-weight: bold;
        color: #2e86c1;
        text-align: center;
    }
    
    .timestamp {
        font-size: 0.8rem;
        color: #7f8c8d;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    .error-box {
        background-color: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid #ef5350;
    }
    
    /* Accessibility improvements */
    .stSelectbox label, .stNumberInput label {
        font-weight: bold;
        color: #333;
    }
    
    /* Focus indicators for accessibility */
    .stNumberInput input:focus, .stSelectbox select:focus {
        outline: 2px solid #2e86c1;
        outline-offset: 2px;
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        .main-title {
            color: #000;
        }
        .conversion-section {
            border: 2px solid #000;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# API configuration - Using a free API that doesn't require authentication
API_URL = "https://open.er-api.com/v6/latest/USD"
TIMEOUT = 10

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def fetch_exchange_rates() -> Optional[Dict]:
    """
    Fetch live currency exchange rates from API.
    
    Returns:
        Dictionary containing exchange rates or None if request fails
    """
    try:
        response = requests.get(API_URL, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        # Check if API returned successful response
        if data.get("result") == "success":
            return data
        else:
            st.error("API returned an unsuccessful response")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Unable to fetch exchange rates: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def convert_currency(amount: float, from_currency: str, to_currency: str, rates: Dict) -> Tuple[float, Optional[str]]:
    """
    Convert between currencies using provided exchange rates.
    
    Args:
        amount: The amount to convert
        from_currency: Source currency code
        to_currency: Target currency code
        rates: Dictionary containing exchange rates
        
    Returns:
        Tuple of (converted_amount, error_message)
    """
    try:
        if from_currency == to_currency:
            return amount, None
        
        if "rates" not in rates or from_currency not in rates["rates"] or to_currency not in rates["rates"]:
            return 0, "Invalid currency selection or missing exchange rates"
        
        # Convert via USD as base currency
        amount_in_usd = amount / rates["rates"][from_currency]
        converted_amount = amount_in_usd * rates["rates"][to_currency]
        
        return round(converted_amount, 4), None
    except (KeyError, ZeroDivisionError, TypeError) as e:
        return 0, f"Conversion error: {str(e)}"

def convert_temperature(amount: float, from_unit: str, to_unit: str) -> Tuple[float, Optional[str]]:
    """
    Convert between temperature units.
    
    Args:
        amount: The temperature value to convert
        from_unit: Source temperature unit
        to_unit: Target temperature unit
        
    Returns:
        Tuple of (converted_temperature, error_message)
    """
    try:
        if from_unit == to_unit:
            return amount, None
        
        # Convert to Celsius first
        if from_unit == "Fahrenheit":
            celsius = (amount - 32) * 5/9
        elif from_unit == "Kelvin":
            celsius = amount - 273.15
        else:  # Celsius
            celsius = amount
        
        # Convert from Celsius to target unit
        if to_unit == "Fahrenheit":
            result = (celsius * 9/5) + 32
        elif to_unit == "Kelvin":
            result = celsius + 273.15
        else:  # Celsius
            result = celsius
        
        return round(result, 2), None
    except Exception as e:
        return 0, f"Temperature conversion error: {str(e)}"

def convert_length(amount: float, from_unit: str, to_unit: str) -> Tuple[float, Optional[str]]:
    """
    Convert between length units.
    
    Args:
        amount: The length value to convert
        from_unit: Source length unit
        to_unit: Target length unit
        
    Returns:
        Tuple of (converted_length, error_message)
    """
    try:
        if from_unit == to_unit:
            return amount, None
        
        # Conversion factors to meters (base unit)
        to_meters = {
            "centimeters": 0.01,
            "meters": 1,
            "kilometers": 1000,
            "inches": 0.0254,
            "feet": 0.3048,
            "miles": 1609.34
        }
        
        if from_unit not in to_meters or to_unit not in to_meters:
            return 0, "Invalid unit selection"
        
        # Convert to meters first
        meters = amount * to_meters[from_unit]
        
        # Convert from meters to target unit
        result = meters / to_meters[to_unit]
        
        return round(result, 4), None
    except Exception as e:
        return 0, f"Length conversion error: {str(e)}"

def convert_weight(amount: float, from_unit: str, to_unit: str) -> Tuple[float, Optional[str]]:
    """
    Convert between weight units.
    
    Args:
        amount: The weight value to convert
        from_unit: Source weight unit
        to_unit: Target weight unit
        
    Returns:
        Tuple of (converted_weight, error_message)
    """
    try:
        if from_unit == to_unit:
            return amount, None
        
        # Conversion factors to grams (base unit)
        to_grams = {
            "grams": 1,
            "kilograms": 1000,
            "pounds": 453.592,
            "ounces": 28.3495
        }
        
        if from_unit not in to_grams or to_unit not in to_grams:
            return 0, "Invalid unit selection"
        
        # Convert to grams first
        grams = amount * to_grams[from_unit]
        
        # Convert from grams to target unit
        result = grams / to_grams[to_unit]
        
        return round(result, 4), None
    except Exception as e:
        return 0, f"Weight conversion error: {str(e)}"

def main():
    """Main application function."""
    st.markdown('<h1 class="main-title">Instant Unit Converter</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'conversion_type' not in st.session_state:
        st.session_state.conversion_type = "Currency"
    
    # Conversion type selector
    conversion_options = ["Currency", "Temperature", "Length", "Weight"]
    conversion_type = st.selectbox(
        "Select Conversion Type",
        options=conversion_options,
        index=conversion_options.index(st.session_state.conversion_type),
        key="conversion_selector",
        help="Choose the type of conversion you want to perform"
    )
    
    st.session_state.conversion_type = conversion_type
    
    st.markdown(f'<div class="conversion-section">', unsafe_allow_html=True)
    st.subheader(f"{conversion_type} Conversion")
    
    # Create columns for input and unit selection
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        amount = st.number_input(
            "Amount", 
            value=1.0, 
            min_value=0.0, 
            step=0.1, 
            key="amount_input",
            help="Enter the value you want to convert"
        )
    
    # Unit selection based on type
    if conversion_type == "Currency":
        currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY"]
        
        with col2:
            from_unit = st.selectbox("From", currencies, key="from_currency", help="Select source currency")
        
        with col3:
            to_unit = st.selectbox("To", currencies, key="to_currency", help="Select target currency")
            
        # Fetch exchange rates
        rates_data = fetch_exchange_rates()
        if rates_data and "rates" in rates_data:
            result, error = convert_currency(amount, from_unit, to_unit, rates_data)
            # Use current time as timestamp if API doesn't provide one
            timestamp = datetime.now()
        else:
            result, error = 0, "Unable to fetch exchange rates. Please try again later."
            timestamp = datetime.now()
            
    elif conversion_type == "Temperature":
        temp_units = ["Celsius", "Fahrenheit", "Kelvin"]
        
        with col2:
            from_unit = st.selectbox("From", temp_units, key="from_temp", help="Select source temperature unit")
        
        with col3:
            to_unit = st.selectbox("To", temp_units, key="to_temp", help="Select target temperature unit")
            
        result, error = convert_temperature(amount, from_unit, to_unit)
        timestamp = datetime.now()
        
    elif conversion_type == "Length":
        length_units = ["centimeters", "meters", "kilometers", "inches", "feet", "miles"]
        
        with col2:
            from_unit = st.selectbox("From", length_units, key="from_length", help="Select source length unit")
        
        with col3:
            to_unit = st.selectbox("To", length_units, key="to_length", help="Select target length unit")
            
        result, error = convert_length(amount, from_unit, to_unit)
        timestamp = datetime.now()
        
    elif conversion_type == "Weight":
        weight_units = ["grams", "kilograms", "pounds", "ounces"]
        
        with col2:
            from_unit = st.selectbox("From", weight_units, key="from_weight", help="Select source weight unit")
        
        with col3:
            to_unit = st.selectbox("To", weight_units, key="to_weight", help="Select target weight unit")
            
        result, error = convert_weight(amount, from_unit, to_unit)
        timestamp = datetime.now()
    
    # Display result or error
    if error:
        st.markdown(f'<div class="error-box">{error}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'''
            <div class="result-box">
                <div class="result-text">{amount} {from_unit} = {result} {to_unit}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        if conversion_type == "Currency":
            st.markdown(f'<div class="timestamp">Rates updated: {timestamp.strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Information section with accessibility info
    with st.expander("ℹ️ About this converter & Accessibility Information"):
        st.write("""
        ## Instant Unit Converter
        
        This app provides real-time conversions for:
        - **Currency**: Uses live exchange rates updated every 30 minutes
        - **Temperature**: Convert between Celsius, Fahrenheit, and Kelvin
        - **Length**: Convert between metric and imperial units
        - **Weight**: Convert between grams, kilograms, pounds, and ounces
        
        ## Accessibility Features
        - High contrast support for better visibility
        - Clear focus indicators for keyboard navigation
        - Descriptive labels for screen readers
        - Responsive design for all device sizes
        
        Results update automatically as you change values or units.
        """)

if __name__ == "__main__":
    main()

# API parameters used:
# - Endpoint URL: https://open.er-api.com/v6/latest/USD (free API, no key required)
# - Timeout: 10 seconds

# Alternative APIs if needed:
# 1. ExchangeRate-API (requires key): https://api.exchangerate-api.com/v4/latest/USD
# 2. Frankfurter (free): https://api.frankfurter.app/latest

# To set up Streamlit secrets for API key (if using an API that requires authentication):
# Create a .streamlit/secrets.toml file with:
# EXCHANGE_RATE_API_KEY = "your_api_key_here"

# Additional Streamlit configuration options (in .streamlit/config.toml):
# [server]
# maxUploadSize = 200
# browser.serverAddress = "0.0.0.0"
# [client]
# showErrorDetails = false