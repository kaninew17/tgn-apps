import streamlit as st
import altair as alt
import pandas as pd
import pyperclip

# ================================
# APP CONFIGURATION
# ================================
st.set_page_config(
    page_title="💱 Currency Converter Pro",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# STATIC EXCHANGE RATES (Base: USD)
# ================================
EXCHANGE_RATES = {
    'USD': 1.0,
    'EUR': 0.85,
    'GBP': 0.73,
    'JPY': 110.0,
    'INR': 82.5
}

CURRENCY_NAMES = {
    'USD': 'US Dollar',
    'EUR': 'Euro',
    'GBP': 'British Pound',
    'JPY': 'Japanese Yen',
    'INR': 'Indian Rupee'
}

CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
    'INR': '₹'
}

# ================================
# CUSTOM CSS STYLING
# ================================
def load_css():
    """Load custom CSS for typography and theming"""
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Roboto:wght@300;400;500&family=Fira+Code:wght@400;500&display=swap');
        
        /* Global Styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Typography */
        .main-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 3rem;
            font-weight: 700;
            color: #333333;
            text-align: center;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #1f77b4, #ff7f0e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .main-subtitle {
            font-family: 'Roboto', sans-serif;
            font-size: 1.2rem;
            color: #666666;
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .section-header {
            font-family: 'Montserrat', sans-serif;
            font-size: 1.5rem;
            font-weight: 600;
            color: #333333;
            margin-bottom: 1rem;
        }
        
        /* Input Controls */
        .stSelectbox label, .stNumberInput label {
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 500 !important;
            color: #333333 !important;
            font-size: 1rem !important;
        }
        
        /* Convert Button */
        .convert-button button {
            font-family: 'Montserrat', sans-serif;
            font-weight: 600;
            background: linear-gradient(135deg, #1f77b4, #ff7f0e);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .convert-button button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        
        /* Result Card */
        .result-card {
            background: linear-gradient(135deg, #f0f2f6, #ffffff);
            border: 2px solid #1f77b4;
            border-radius: 15px;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        .result-amount {
            font-family: 'Montserrat', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: #1f77b4;
            margin: 1rem 0;
        }
        
        .result-text {
            font-family: 'Roboto', sans-serif;
            font-size: 1.1rem;
            color: #666666;
            margin-bottom: 1rem;
        }
        
        /* Copy Button */
        .copy-button button {
            font-family: 'Montserrat', sans-serif;
            background: #ff7f0e;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .copy-button button:hover {
            background: #e6720d;
            transform: scale(1.05);
        }
        
        /* Sidebar Styling */
        .sidebar .sidebar-content {
            background: #f8f9fa;
        }
        
        /* Currency Table */
        .currency-table {
            font-family: 'Roboto', sans-serif;
            background: white;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Theme Toggle */
        .theme-toggle {
            font-family: 'Montserrat', sans-serif;
            margin-bottom: 2rem;
        }
        
        /* Error Messages */
        .error-message {
            background: #fee;
            color: #c33;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #c33;
            font-family: 'Roboto', sans-serif;
            margin: 1rem 0;
        }
        
        /* Success Messages */
        .success-message {
            background: #efe;
            color: #363;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #363;
            font-family: 'Roboto', sans-serif;
            margin: 1rem 0;
        }
        
        /* Chart Container */
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin: 2rem 0;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .main-title {
                font-size: 2rem;
            }
            
            .result-amount {
                font-size: 2rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# ================================
# SESSION STATE INITIALIZATION
# ================================
def initialize_session_state():
    """Initialize session state variables"""
    if 'theme' not in st.session_state:
        st.session_state['theme'] = 'light'
    if 'last_conversion' not in st.session_state:
        st.session_state['last_conversion'] = None

# ================================
# UTILITY FUNCTIONS
# ================================
def convert_currency(amount, from_currency, to_currency):
    """Convert amount from one currency to another"""
    if from_currency == to_currency:
        return amount
    
    # Convert to USD first, then to target currency
    usd_amount = amount / EXCHANGE_RATES[from_currency]
    converted_amount = usd_amount * EXCHANGE_RATES[to_currency]
    
    return round(converted_amount, 2)

def validate_amount(amount):
    """Validate the input amount"""
    if amount is None:
        return False, "Please enter an amount"
    if amount < 0:
        return False, "Amount cannot be negative"
    if amount == 0:
        return False, "Amount must be greater than zero"
    if amount > 1e15:
        return False, "Amount is too large"
    return True, ""

def copy_to_clipboard(text):
    """Copy text to clipboard"""
    try:
        pyperclip.copy(text)
        return True
    except:
        return False

def format_currency(amount, currency):
    """Format currency with proper symbol and decimals"""
    symbol = CURRENCY_SYMBOLS[currency]
    
    if currency == 'JPY':
        # Japanese Yen typically doesn't use decimals
        return f"{symbol}{amount:,.0f}"
    else:
        return f"{symbol}{amount:,.2f}"

# ================================
# UI COMPONENTS
# ================================
def render_sidebar():
    """Render sidebar with theme toggle and currency rates table"""
    with st.sidebar:
        st.markdown('<div class="theme-toggle">', unsafe_allow_html=True)
        st.markdown("### 🎨 Theme")
        
        theme = st.radio(
            "Choose theme:",
            ["Light", "Dark"],
            index=0 if st.session_state['theme'] == 'light' else 1,
            horizontal=True
        )
        
        if theme.lower() != st.session_state['theme']:
            st.session_state['theme'] = theme.lower()
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Currency Rates Table
        st.markdown("### 📊 Current Exchange Rates")
        st.markdown("*Base: 1 USD*")
        
        # Create rates dataframe
        rates_data = []
        for currency, rate in EXCHANGE_RATES.items():
            rates_data.append({
                'Currency': f"{CURRENCY_SYMBOLS[currency]} {currency}",
                'Name': CURRENCY_NAMES[currency],
                'Rate': f"{rate:,.4f}" if currency != 'USD' else "1.0000"
            })
        
        rates_df = pd.DataFrame(rates_data)
        
        st.markdown('<div class="currency-table">', unsafe_allow_html=True)
        st.dataframe(
            rates_df,
            use_container_width=True,
            hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Info
        st.markdown("---")
        st.markdown("### ℹ️ Quick Info")
        st.markdown("""
        - **Live rates**: Static demo rates
        - **Precision**: 2 decimal places
        - **Base currency**: USD
        - **Copy feature**: Available for results
        """)

def render_main_header():
    """Render main application header"""
    st.markdown("""
    <div class="main-title">💱 Currency Converter Pro</div>
    <div class="main-subtitle">Convert between major world currencies instantly with beautiful visualizations</div>
    """, unsafe_allow_html=True)

def render_conversion_interface():
    """Render the main conversion interface"""
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('<div class="section-header">🔄 Convert Currency</div>', unsafe_allow_html=True)
        
        # Currency selection
        from_currency = st.selectbox(
            "From Currency:",
            options=list(EXCHANGE_RATES.keys()),
            format_func=lambda x: f"{CURRENCY_SYMBOLS[x]} {x} - {CURRENCY_NAMES[x]}",
            key="from_currency"
        )
        
        to_currency = st.selectbox(
            "To Currency:",
            options=list(EXCHANGE_RATES.keys()),
            format_func=lambda x: f"{CURRENCY_SYMBOLS[x]} {x} - {CURRENCY_NAMES[x]}",
            key="to_currency",
            index=1  # Default to second currency
        )
        
        # Amount input
        amount = st.number_input(
            "Amount:",
            min_value=0.0,
            step=1.0,
            format="%.2f",
            help="Enter the amount you want to convert"
        )
        
        # Convert button
        st.markdown('<div class="convert-button">', unsafe_allow_html=True)
        convert_clicked = st.button("🚀 Convert Currency", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header">💰 Result</div>', unsafe_allow_html=True)
        
        if convert_clicked:
            # Validate input
            is_valid, error_message = validate_amount(amount)
            
            if not is_valid:
                st.markdown(f"""
                <div class="error-message">
                    <strong>❌ Error:</strong> {error_message}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Perform conversion
                converted_amount = convert_currency(amount, from_currency, to_currency)
                
                # Store in session state
                st.session_state['last_conversion'] = {
                    'from_amount': amount,
                    'from_currency': from_currency,
                    'to_amount': converted_amount,
                    'to_currency': to_currency,
                    'rate': EXCHANGE_RATES[to_currency] / EXCHANGE_RATES[from_currency]
                }
        
        # Display result if available
        if st.session_state['last_conversion']:
            conv = st.session_state['last_conversion']
            
            formatted_result = format_currency(conv['to_amount'], conv['to_currency'])
            formatted_input = format_currency(conv['from_amount'], conv['from_currency'])
            
            st.markdown(f"""
            <div class="result-card">
                <div class="result-text">
                    {formatted_input} equals
                </div>
                <div class="result-amount">
                    {formatted_result}
                </div>
                <div class="result-text">
                    Exchange rate: 1 {conv['from_currency']} = {conv['rate']:.4f} {conv['to_currency']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Copy button
            st.markdown('<div class="copy-button">', unsafe_allow_html=True)
            if st.button("📋 Copy Result", use_container_width=True):
                copy_text = f"{formatted_input} = {formatted_result}"
                if copy_to_clipboard(copy_text):
                    st.success("✅ Copied to clipboard!")
                else:
                    st.warning("⚠️ Copy to clipboard not available in this environment")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="result-card">
                <div class="result-text">
                    Enter an amount and click convert to see the result
                </div>
                <div style="font-size: 4rem; color: #cccccc; margin: 2rem 0;">
                    💱
                </div>
                <div class="result-text">
                    Ready to convert currencies
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_exchange_rates_chart():
    """Render interactive bar chart of exchange rates"""
    st.markdown('<div class="section-header">📈 Exchange Rates Visualization</div>', unsafe_allow_html=True)
    
    # Prepare data for chart
    chart_data = []
    for currency, rate in EXCHANGE_RATES.items():
        if currency != 'USD':  # Exclude USD as it's the base
            chart_data.append({
                'Currency': f"{CURRENCY_SYMBOLS[currency]} {currency}",
                'Rate': rate,
                'Full_Name': CURRENCY_NAMES[currency]
            })
    
    df_chart = pd.DataFrame(chart_data)
    
    # Create Altair chart
    chart = alt.Chart(df_chart).mark_bar(
        color='#1f77b4',
        cornerRadiusTopLeft=5,
        cornerRadiusTopRight=5
    ).add_selection(
        alt.selection_single()
    ).encode(
        x=alt.X('Currency:O', 
               title='Currency',
               sort=alt.EncodingSortField(field='Rate', order='descending')),
        y=alt.Y('Rate:Q', 
               title='Exchange Rate (vs USD)',
               scale=alt.Scale(domain=[0, max(EXCHANGE_RATES.values()) * 1.1])),
        tooltip=[
            alt.Tooltip('Currency:O', title='Currency'),
            alt.Tooltip('Full_Name:O', title='Full Name'),
            alt.Tooltip('Rate:Q', title='Rate (vs USD)', format='.4f')
        ],
        color=alt.condition(
            alt.selection_single(),
            alt.value('#ff7f0e'),  # Highlighted color
            alt.value('#1f77b4')   # Default color
        )
    ).properties(
        width=600,
        height=400,
        title=alt.TitleParams(
            text="Exchange Rates Relative to USD",
            fontSize=16,
            fontWeight='bold',
            color='#333333'
        )
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        titleColor='#333333',
        labelColor='#666666'
    ).configure_title(
        fontSize=18,
        fontWeight='bold',
        color='#333333'
    )
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.altair_chart(chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chart explanation
    st.markdown("""
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
        <strong>💡 Chart Explanation:</strong><br>
        • Bars show how many units of each currency equal 1 USD<br>
        • Higher bars = weaker currency (more units needed for 1 USD)<br>
        • Click on bars to highlight them<br>
        • Hover for detailed information
    </div>
    """, unsafe_allow_html=True)

# ================================
# MAIN APPLICATION
# ================================
def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Load custom CSS
    load_css()
    
    # Apply theme-specific styling
    if st.session_state['theme'] == 'dark':
        st.markdown("""
        <style>
            .main-title { color: #ffffff !important; }
            .main-subtitle { color: #cccccc !important; }
            .section-header { color: #ffffff !important; }
            .result-card { background: linear-gradient(135deg, #2d3748, #4a5568) !important; }
            .currency-table { background: #2d3748 !important; color: #ffffff !important; }
        </style>
        """, unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    with st.container():
        # App header
        render_main_header()
        
        # Conversion interface
        render_conversion_interface()
        
        # Separator
        st.markdown("---")
        
        # Exchange rates chart
        render_exchange_rates_chart()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666666; font-family: 'Roboto', sans-serif; padding: 2rem 0;">
            <strong>💱 Currency Converter Pro</strong> | Built with ❤️ using Streamlit & Altair<br>
            <small>Demo application with static exchange rates for educational purposes</small>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()