###############################
# Burger Buddy — Order & Billing
# Quickstart:
#   pip install streamlit reportlab pandas
#   streamlit run app.py
###############################

import streamlit as st
import pandas as pd
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import uuid
import io

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# -------------------------
# Utils
# -------------------------

def _round(val: Decimal) -> Decimal:
    return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def format_money(amount: float) -> str:
    return f"${amount:,.2f}"

def generate_invoice_id() -> str:
    return str(uuid.uuid4())[:8]

# -------------------------
# Menu Data
# -------------------------

def load_menu():
    return [
        {"id": "classic_burger", "name": "Classic Burger 🍔", "desc": "Juicy beef patty", "price": 5.99, "category": "Burgers", "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=400&fit=crop&crop=center"},
        {"id": "cheeseburger", "name": "Cheeseburger 🧀🍔", "desc": "With cheddar", "price": 6.99, "category": "Burgers", "image": "https://images.unsplash.com/photo-1553979459-d2229ba7433a?w=400&h=400&fit=crop&crop=center"},
        {"id": "veggie_burger", "name": "Veggie Burger 🥦🍔", "desc": "Plant-based patty", "price": 6.49, "category": "Burgers", "image": "https://images.unsplash.com/photo-1525059696034-4967a729002e?w=400&h=400&fit=crop&crop=center"},
        {"id": "fries", "name": "Fries 🍟", "desc": "Golden crispy fries", "price": 2.49, "category": "Sides", "image": "https://images.unsplash.com/photo-1576107232684-1279f390859f?w=400&h=400&fit=crop&crop=center"},
        {"id": "onion_rings", "name": "Onion Rings 🧅", "desc": "Crispy battered rings", "price": 2.99, "category": "Sides", "image": "https://images.unsplash.com/photo-1639024471283-03518883512d?w=400&h=400&fit=crop&crop=center"},
        {"id": "soda", "name": "Soda 🥤", "desc": "Choice of cola, lemon", "price": 1.99, "category": "Drinks", "image": "https://images.unsplash.com/photo-1581636625402-29b2a704ef13?w=400&h=400&fit=crop&crop=center"},
        {"id": "iced_tea", "name": "Iced Tea 🧊🍵", "desc": "Fresh brewed", "price": 2.29, "category": "Drinks", "image": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&h=400&fit=crop&crop=center"},
        {"id": "milkshake", "name": "Milkshake 🥤🍦", "desc": "Vanilla or chocolate", "price": 3.99, "category": "Drinks", "image": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400&h=400&fit=crop&crop=center"},
        {"id": "brownie", "name": "Brownie 🍫", "desc": "Chocolate fudge", "price": 2.49, "category": "Desserts", "image": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=400&h=400&fit=crop&crop=center"},
        {"id": "ice_cream", "name": "Ice Cream 🍨", "desc": "Two scoops", "price": 2.99, "category": "Desserts", "image": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=400&fit=crop&crop=center"},
    ]

MENU = load_menu()
MENU_LOOKUP = {item["id"]: item for item in MENU}

# -------------------------
# Cart Logic
# -------------------------

def init_cart():
    if "cart" not in st.session_state:
        st.session_state.cart = {}

def add_to_cart(item_id: str, qty: int = 1):
    item = MENU_LOOKUP[item_id]
    if item_id not in st.session_state.cart:
        st.session_state.cart[item_id] = {
            "name": item["name"],
            "unit_price": item["price"],
            "qty": 0,
        }
    st.session_state.cart[item_id]["qty"] += qty
    if st.session_state.cart[item_id]["qty"] <= 0:
        st.session_state.cart.pop(item_id)

def clear_cart():
    st.session_state.cart.clear()

# -------------------------
# Invoice Generation
# -------------------------

def build_invoice(cart: dict, tax_rate: float, tip: float):
    subtotal = sum(v["unit_price"] * v["qty"] for v in cart.values())
    tax = subtotal * tax_rate / 100
    total = subtotal + tax + tip
    return {
        "invoice_id": generate_invoice_id(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": cart.copy(),
        "subtotal": subtotal,
        "tax": tax,
        "tip": tip,
        "total": total,
    }

def invoice_to_csv(invoice: dict) -> bytes:
    rows = []
    for k, v in invoice["items"].items():
        rows.append({"Item": v["name"], "Unit Price": v["unit_price"], "Qty": v["qty"], "Line Total": v["unit_price"]*v["qty"]})
    df = pd.DataFrame(rows)
    df.loc["Subtotal"] = ["", "", "", invoice["subtotal"]]
    df.loc["Tax"] = ["", "", "", invoice["tax"]]
    df.loc["Tip"] = ["", "", "", invoice["tip"]]
    df.loc["Total"] = ["", "", "", invoice["total"]]
    return df.to_csv(index=False).encode("utf-8")

def invoice_to_pdf(invoice: dict) -> bytes | None:
    if not REPORTLAB_AVAILABLE:
        return None
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Burger Buddy — Invoice")
    c.setFont("Helvetica", 10)
    c.drawString(50, 735, f"Invoice ID: {invoice['invoice_id']}  Date: {invoice['timestamp']}")

    y = 700
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Item")
    c.drawString(250, y, "Qty")
    c.drawString(300, y, "Unit")
    c.drawString(380, y, "Total")
    c.setFont("Helvetica", 12)
    y -= 20
    for v in invoice["items"].values():
        c.drawString(50, y, v["name"])
        c.drawString(250, y, str(v["qty"]))
        c.drawString(300, y, format_money(v["unit_price"]))
        c.drawString(380, y, format_money(v["unit_price"]*v["qty"]))
        y -= 20

    y -= 10
    c.line(50, y, 500, y)
    y -= 20
    c.drawString(300, y, "Subtotal:")
    c.drawString(380, y, format_money(invoice["subtotal"]))
    y -= 20
    c.drawString(300, y, "Tax:")
    c.drawString(380, y, format_money(invoice["tax"]))
    y -= 20
    c.drawString(300, y, "Tip:")
    c.drawString(380, y, format_money(invoice["tip"]))
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, y, "Total:")
    c.drawString(380, y, format_money(invoice["total"]))

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()

# -------------------------
# UI
# -------------------------

def render_menu():
    st.subheader("Menu")
    cols = st.columns(2)
    for idx, item in enumerate(MENU):
        with cols[idx % 2]:
            st.image(item["image"], width=200)
            st.markdown(f"#### {item['name']}")
            st.caption(item["desc"])
            st.write(format_money(item["price"]))
            qty = st.number_input("Qty", 1, 10, 1, key=f"qty_{item['id']}")
            if st.button("Add", key=f"add_{item['id']}"):
                add_to_cart(item["id"], qty)
                st.success(f"Added {qty} × {item['name']} to cart")

def render_cart_sidebar():
    st.sidebar.subheader("🛒 Cart")
    if not st.session_state.cart:
        st.sidebar.info("Your cart is empty.")
        return

    for k, v in st.session_state.cart.items():
        cols = st.sidebar.columns([4, 2, 4, 1])
        cols[0].markdown(f"**{v['name']}**")
        cols[1].markdown(f"{format_money(v['unit_price'])}")
        cols[2].markdown(
            f"Qty: **{v['qty']}**  <br>Line: **{format_money(_round(Decimal(v['unit_price'])*Decimal(v['qty'])))}**",
            unsafe_allow_html=True,
        )
        if cols[3].button("❌", key=f"remove_{k}"):
            st.session_state.cart.pop(k)
            st.experimental_rerun()

    st.sidebar.markdown("---")
    tax_rate = st.sidebar.number_input("Tax %", 0.0, 20.0, 8.5)
    tip = st.sidebar.number_input("Tip $", 0.0, 100.0, 0.0)

    invoice = build_invoice(st.session_state.cart, tax_rate, tip)
    st.sidebar.write("Subtotal:", format_money(invoice["subtotal"]))
    st.sidebar.write("Tax:", format_money(invoice["tax"]))
    st.sidebar.write("Tip:", format_money(invoice["tip"]))
    st.sidebar.write("**Total:**", format_money(invoice["total"]))

    if st.sidebar.button("Place Order"):
        st.balloons()
        st.session_state.last_invoice = invoice
        clear_cart()
        st.sidebar.success(f"Order placed! Invoice {invoice['invoice_id']}")

    if "last_invoice" in st.session_state:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📄 Last Invoice")
        inv = st.session_state.last_invoice
        csv_bytes = invoice_to_csv(inv)
        st.sidebar.download_button("Download CSV", csv_bytes, file_name=f"invoice_{inv['invoice_id']}.csv")
        pdf_bytes = invoice_to_pdf(inv)
        if pdf_bytes:
            st.sidebar.download_button("Download PDF", pdf_bytes, file_name=f"invoice_{inv['invoice_id']}.pdf")
        else:
            st.sidebar.warning("PDF export requires reportlab (pip install reportlab)")

# -------------------------
# Main
# -------------------------

def main():
    st.set_page_config(page_title="Burger Buddy — Order & Billing", layout="wide")
    
    # Add custom CSS for attractive fonts and better readability
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }
        
        .main .block-container {
            font-family: 'Poppins', sans-serif;
        }
        
        h1 {
            font-family: 'Poppins', sans-serif !important;
            font-weight: 700 !important;
            font-size: 2.5rem !important;
            color: #2c3e50 !important;
        }
        
        h2 {
            font-family: 'Poppins', sans-serif !important;
            font-weight: 600 !important;
            font-size: 1.8rem !important;
            color: #34495e !important;
        }
        
        h3, h4 {
            font-family: 'Poppins', sans-serif !important;
            font-weight: 600 !important;
            font-size: 1.3rem !important;
            color: #2c3e50 !important;
        }
        
        p, div, span {
            font-family: 'Poppins', sans-serif !important;
            font-size: 1.1rem !important;
            line-height: 1.6 !important;
        }
        
        .stButton > button {
            font-family: 'Poppins', sans-serif !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
        }
        
        .stNumberInput > div > div > input {
            font-family: 'Poppins', sans-serif !important;
            font-size: 1rem !important;
        }
        
        .stCaption {
            font-family: 'Poppins', sans-serif !important;
            font-size: 1rem !important;
            color: #7f8c8d !important;
        }
        
        .sidebar .sidebar-content {
            font-family: 'Poppins', sans-serif !important;
        }
        
        .sidebar h2, .sidebar h3 {
            font-family: 'Poppins', sans-serif !important;
            font-weight: 600 !important;
            font-size: 1.4rem !important;
        }
        
        .sidebar p, .sidebar div {
            font-family: 'Poppins', sans-serif !important;
            font-size: 1rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🍔 Burger Buddy — Order & Billing")
    init_cart()
    render_menu()
    render_cart_sidebar()

if __name__ == "__main__":
    main()