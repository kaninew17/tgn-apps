import streamlit as st
import pandas as pd

def main():
    st.set_page_config(
        page_title="FairSplit - Expense Splitter",
        page_icon="💰",
        layout="centered"
    )
    
    st.title("💰 FairSplit - Expense Splitter")
    st.markdown("### Split expenses fairly among friends after dinners, trips, or any group activities!")
    
    # Initialize session state
    if 'people_data' not in st.session_state:
        st.session_state.people_data = []
    if 'num_people' not in st.session_state:
        st.session_state.num_people = 0
    if 'total_amount' not in st.session_state:
        st.session_state.total_amount = 0.0
    if 'calculation_done' not in st.session_state:
        st.session_state.calculation_done = False
    
    # Main form for total amount and number of people
    with st.form("basic_info"):
        st.subheader("Step 1: Enter Bill Details")
        total_amount = st.number_input(
            "Total Amount ($)",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            help="Enter the total bill amount"
        )
        
        num_people = st.number_input(
            "Number of People",
            min_value=1,
            step=1,
            help="How many people to split between?"
        )
        
        submitted_basic = st.form_submit_button("Continue to Enter Contributions")
        
        if submitted_basic:
            st.session_state.total_amount = total_amount
            st.session_state.num_people = num_people
            st.session_state.people_data = [{"name": "", "paid": 0.0} for _ in range(num_people)]
            st.session_state.calculation_done = False
            st.rerun()
    
    # Display people input form if basic info is submitted
    if st.session_state.num_people > 0:
        st.divider()
        st.subheader(f"Step 2: Enter Details for {st.session_state.num_people} People")
        
        with st.form("people_details"):
            # Create input fields for each person
            for i in range(st.session_state.num_people):
                col1, col2 = st.columns([2, 1])
                with col1:
                    name = st.text_input(
                        f"Person {i+1} Name",
                        value=st.session_state.people_data[i]["name"],
                        key=f"name_{i}",
                        placeholder="Enter name"
                    )
                with col2:
                    paid = st.number_input(
                        "Amount Paid ($)",
                        min_value=0.0,
                        step=0.01,
                        format="%.2f",
                        value=st.session_state.people_data[i]["paid"],
                        key=f"paid_{i}",
                        help=f"Amount paid by {name if name else 'this person'}"
                    )
                
                st.session_state.people_data[i] = {"name": name, "paid": paid}
            
            submitted_details = st.form_submit_button("Calculate Fair Split")
            
            if submitted_details:
                # Validate that names are entered
                if any(not person["name"].strip() for person in st.session_state.people_data):
                    st.error("Please enter a name for each person.")
                else:
                    st.session_state.calculation_done = True
                    st.rerun()
    
    # Calculate and display results
    if st.session_state.calculation_done and st.session_state.people_data:
        st.divider()
        st.subheader("Step 3: Results")
        
        # Calculate fair share and balances
        fair_share = st.session_state.total_amount / st.session_state.num_people
        results = []
        
        for person in st.session_state.people_data:
            balance = person["paid"] - fair_share
            results.append({
                "Name": person["name"],
                "Paid": f"${person['paid']:.2f}",
                "Fair Share": f"${fair_share:.2f}",
                "Balance": balance
            })
        
        # Create DataFrame for display
        df = pd.DataFrame(results)
        df_display = df.copy()
        df_display["Balance"] = df["Balance"].apply(lambda x: f"${abs(x):.2f}")
        
        # Display the results table with conditional formatting
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
        
        # Display summary statements
        st.subheader("Summary")
        for person in results:
            name = person["Name"]
            balance = person["Balance"]
            
            if balance > 0:
                st.success(f"✅ {name} gets back ${balance:.2f}")
            elif balance < 0:
                st.error(f"❌ {name} owes ${abs(balance):.2f}")
            else:
                st.info(f"⚖️ {name} is all settled up!")
        
        # Add a reset button
        if st.button("Start Over"):
            st.session_state.people_data = []
            st.session_state.num_people = 0
            st.session_state.total_amount = 0.0
            st.session_state.calculation_done = False
            st.rerun()

if __name__ == "__main__":
    main()
