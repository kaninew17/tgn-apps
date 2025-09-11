import streamlit as st

# Set page configuration for a professional, centered layout
st.set_page_config(page_title="BMI Calculator", layout="centered")

# --- UI Layout and Widgets ---

# Main header
st.title("BMI Calculator")
st.markdown("### Find out your Body Mass Index and what it means for your health.")

# Use columns for a clean, side-by-side layout
col1, col2 = st.columns(2)

with col1:
    height_cm = st.number_input("Enter your height (in cm)", min_value=1.0, value=170.0, step=1.0)

with col2:
    weight_kg = st.number_input("Enter your weight (in kg)", min_value=1.0, value=70.0, step=0.1)

# A simple button to trigger the calculation
if st.button("Calculate BMI", help="Click to calculate your BMI"):
    if height_cm > 0 and weight_kg > 0:
        # --- Core Logic ---
        
        # Convert height from cm to meters
        height_m = height_cm / 100.0
        
        # Calculate BMI using the formula: kg/m^2
        bmi = weight_kg / (height_m ** 2)
        
        # --- Result and Feedback ---
        st.write("") # Add some space
        st.metric(label="Your BMI", value=f"{bmi:.2f} kg/m²")

        # Determine the BMI category and associated feedback
        category = ""
        color = ""
        if bmi < 18.5:
            category = "Underweight"
            color = "#ff4b4b"  # Red
            st.info("You are in the Underweight range. It's recommended to consult a professional for personalized advice.")
            
        elif 18.5 <= bmi < 24.9:
            category = "Normal Weight"
            color = "#00b200"  # Green
            st.success("You are in the Normal weight range. Great job!")
            
        elif 25 <= bmi < 29.9:
            category = "Overweight"
            color = "#ff8c00"  # Orange
            st.warning("You are in the Overweight range. A healthy diet and exercise can make a difference.")
            
        else: # bmi >= 30
            category = "Obese"
            color = "#ff0000"  # Dark Red
            st.error("You are in the Obese range. It is advisable to seek guidance from a healthcare professional.")

        st.markdown(f"#### Status: **{category}**")

        # --- Visual BMI Meter ---
        st.markdown(
            f"""
            <style>
            .bmi-meter-container {{
                width: 100%;
                background-color: #f0f2f6;
                border-radius: 10px;
                overflow: hidden;
                margin-top: 20px;
            }}
            .bmi-meter-bar {{
                height: 30px;
                background-color: {color};
                width: {min(100, (bmi / 40) * 100)}%; /* Scale BMI value to a percentage */
                transition: width 0.5s ease-in-out;
            }}
            </style>
            <div class="bmi-meter-container">
                <div class="bmi-meter-bar"></div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        # --- Relevant Article Links (Placeholder for real-time search) ---
        st.subheader("Relevant Articles from World-Famous Nutritionists")
        
        # Placeholder links that align with the user's BMI category.
        if bmi < 18.5:
            st.markdown(
                """
                - **[Dr. A's Guide to Healthy Weight Gain](https://www.dr-a.com/healthy-gain)**
                  > An article on nutritional strategies and safe weight gain practices.
                - **[The B Clinic's Best Practices for Underweight Individuals](https://www.thebclinic.org/underweight-tips)**
                  > Expert advice on improving diet and muscle mass.
                - **[C. Journal's Study on Malnutrition Risks](https://www.c-journal.edu/malnutrition-study)**
                  > A scientific look at the health risks associated with a low BMI.
                """
            )
        elif 18.5 <= bmi < 24.9:
            st.markdown(
                """
                - **[Dr. A's Guide to Maintaining a Healthy Weight](https://www.dr-a.com/weight-maintenance)**
                  > Tips and tricks for keeping a healthy lifestyle.
                - **[The B Clinic's Nutritional Strategies for Wellness](https://www.thebclinic.org/wellness-tips)**
                  > Practical dietary tips and meal plans for long-term health.
                - **[C. Journal's Study on Optimal Health](https://www.c-journal.edu/optimal-health-study)**
                  > An analysis of factors contributing to a healthy life, beyond just BMI.
                """
            )
        elif 25 <= bmi < 29.9:
            st.markdown(
                """
                - **[Dr. A's Guide to Healthy Weight Management](https://www.dr-a.com/weight-management)**
                  > An in-depth article on sustainable habits for reducing BMI.
                - **[The B Clinic's Nutritional Strategies for Overweight Individuals](https://www.thebclinic.org/overweight-tips)**
                  > Expert advice on healthy diet and exercise routines.
                - **[C. Journal's Study on Body Composition and Health Risks](https://www.c-journal.edu/body-composition-study)**
                  > A scientific look at the connection between body fat and health.
                """
            )
        else: # bmi >= 30
            st.markdown(
                """
                - **[Dr. A's Guide to Weight Loss and Health](https://www.dr-a.com/weight-loss)**
                  > Strategies for safe and effective weight loss.
                - **[The B Clinic's Expert Guidance on Obesity](https://www.thebclinic.org/obesity-tips)**
                  > Information on how to manage and reduce health risks.
                - **[C. Journal's Study on Obesity-Related Diseases](https://www.c-journal.edu/obesity-study)**
                  > A scientific analysis of the health issues linked to obesity.
                """
            )

        st.markdown("---")

        # --- Notes on BMI's Limitations ---
        st.subheader("Important Notes on BMI")
        st.markdown(
            """
            * **BMI Doesn't Measure Body Fat Directly:** BMI is a simple ratio of weight to height. It doesn't distinguish between muscle, bone, or fat, which means a very muscular person can be classified as overweight or obese.
            * **Ignores Fat Distribution:** It doesn't account for where fat is stored. Abdominal fat is a greater health risk than fat stored elsewhere, and BMI can't detect this.
            * **Demographic Inaccuracies:** The standard BMI scale is not always accurate for all ethnic groups or age ranges. It is also unsuitable for specific populations like pregnant women.
            * **Not a Health Indicator:** A person's BMI doesn't necessarily reflect their overall health. Individuals with a "normal" BMI may have health issues, while someone with a high BMI could be very physically fit.
            * **Sarcopenia Misclassification:** BMI can underestimate body fat in older adults or people who have lost muscle mass, a condition called sarcopenia, because their total weight may be lower despite a higher percentage of body fat.
            """
        )
