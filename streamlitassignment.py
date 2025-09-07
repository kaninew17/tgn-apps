# streamlit_resume_builder.py
import streamlit as st
from fpdf import FPDF
from PIL import Image
from io import BytesIO
import textwrap
import datetime

st.set_page_config(page_title="Nurse Resume Builder", layout="wide")

# ---------- Helpers ----------
MAX_PHOTO_BYTES = 1_000_000  # 1 MB

def bytes_size_ok(uploaded_file) -> bool:
    if not uploaded_file:
        return False
    try:
        return uploaded_file.size <= MAX_PHOTO_BYTES
    except Exception:
        uploaded_file.seek(0, 2)
        size = uploaded_file.tell()
        uploaded_file.seek(0)
        return size <= MAX_PHOTO_BYTES

# ---------- PDF Generation ----------
def generate_pdf(data: dict, photo_bytes: bytes) -> bytes:
    """
    Generate a simple, clean PDF resume using fpdf2 with Unicode font.
    Returns PDF bytes.
    """
    pdf = FPDF(format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # --- Add Unicode font ---
    # Make sure DejaVuSans.ttf is in the same folder as this script
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSans.ttf', uni=True)

    # Header: name and contact
    pdf.set_font('DejaVu', 'B', 18)
    pdf.cell(0, 8, txt=data['full_name'], ln=1)
    pdf.set_font('DejaVu', '', 10)
    contact = f"{data['phone']}  |  {data['email']}  |  {data['city_state']}"
    pdf.cell(0, 6, txt=contact, ln=1)
    pdf.ln(4)

    # Insert photo on the right top if present
    if photo_bytes:
        try:
            img = Image.open(BytesIO(photo_bytes)).convert("RGB")
            max_w = 120
            w_percent = max_w / float(img.size[0])
            h_size = int(float(img.size[1]) * float(w_percent))
            img = img.resize((max_w, h_size))
            bio = BytesIO()
            img.save(bio, format="JPEG")
            bio.seek(0)
            x_position = 150
            y_position = 10
            pdf.image(bio, x=x_position, y=y_position, w=35)
        except Exception:
            pass

    pdf.ln(4)

    # Professional summary
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 8, txt="Professional Summary", ln=1)
    pdf.set_font('DejaVu', '', 11)
    for line in textwrap.wrap(data['summary'], width=100):
        pdf.multi_cell(0, 6, line)
    pdf.ln(2)

    # Education
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 8, txt="Education", ln=1)
    pdf.set_font('DejaVu', '', 11)
    edu_line = f"{data['degree']} — {data['institution']} ({data['graduation_date']})"
    pdf.multi_cell(0, 6, edu_line)
    pdf.ln(2)

    # Licenses & Certifications
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 8, txt="Licenses & Certifications", ln=1)
    pdf.set_font('DejaVu', '', 11)
    pdf.multi_cell(0, 6, f"License Number: {data['license_number']}")
    pdf.ln(2)

    # Professional Experience
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 8, txt="Professional Experience", ln=1)
    pdf.set_font('DejaVu', '', 11)
    pdf.multi_cell(0, 6, f"Job Title: {data['job_title']}")
    pdf.ln(1)
    duties = [d.strip() for d in data['duties'].splitlines() if d.strip()]
    for duty in duties:
        wrapped = textwrap.wrap(duty, width=95)
        if wrapped:
            pdf.cell(6)  # small indent for bullet
            pdf.cell(2, 5, txt="•")
            pdf.multi_cell(0, 6, " " + wrapped[0])
            for cont in wrapped[1:]:
                pdf.cell(8)
                pdf.multi_cell(0, 6, cont)
    pdf.ln(2)

    # Skills
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 8, txt="Skills", ln=1)
    pdf.set_font('DejaVu', '', 11)
    hard = ", ".join([s.strip() for s in data['hard_skills'].split(",") if s.strip()])
    soft = ", ".join([s.strip() for s in data['soft_skills'].split(",") if s.strip()])
    pdf.multi_cell(0, 6, f"Hard Skills: {hard}")
    pdf.multi_cell(0, 6, f"Soft Skills: {soft}")
    pdf.ln(6)

    # Footer: generation timestamp
    pdf.set_font('DejaVu', '', 9)
    pdf.cell(0, 8, txt=f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1, align='R')

    return pdf.output(dest='S').encode('latin-1')

# ---------- UI ----------
st.title("🩺 Nurse Resume Builder — Streamlit")

col1, col2 = st.columns([2, 1])
with col1:
    st.header("Enter your details")

    full_name = st.text_input("Full Name", value="")
    phone = st.text_input("Phone Number", value="")
    email = st.text_input("Email Address", value="")
    city_state = st.text_input("City, State", value="")

    st.subheader("Professional Summary")
    summary = st.text_area("Write a short professional summary", height=120)

    st.subheader("Photo Upload")
    photo_file = st.file_uploader("Upload professional photo (≤ 1 MB)", type=["png", "jpg", "jpeg"])
    photo_ok = None
    if photo_file:
        if bytes_size_ok(photo_file):
            photo_ok = True
            try:
                st.image(photo_file, caption="Uploaded photo preview", width=150)
            except Exception:
                st.write("Preview not available.")
        else:
            photo_ok = False
            st.error("Photo must be 1 MB or smaller. Please upload a smaller image.")
    else:
        st.info("No photo uploaded yet.")

    st.subheader("Education")
    degree = st.text_input("Degree / Qualification", value="")
    institution = st.text_input("University / Institution", value="")
    graduation_date = st.text_input("Graduation Date (e.g., 2020 or May 2020)", value="")

    st.subheader("Licenses & Certifications")
    license_number = st.text_input("License Number", value="")

    st.subheader("Professional Experience")
    job_title = st.text_input("Most Recent Job Title", value="")
    duties = st.text_area("Duties & Achievements (one per line)", height=140)

    st.subheader("Skills (comma-separated)")
    hard_skills = st.text_input("Hard Skills (e.g., Phlebotomy, EKG)", value="")
    soft_skills = st.text_input("Soft Skills (e.g., Communication, Empathy)", value="")

    # Validation: all fields mandatory
    required_values = [
        full_name, phone, email, city_state, summary,
        photo_file, degree, institution, graduation_date,
        license_number, job_title, duties, hard_skills, soft_skills
    ]
    all_filled = all([(v is not None and (not isinstance(v, str) or v.strip() != "")) for v in required_values])
    if photo_file and not photo_ok:
        all_filled = False

    st.markdown("---")

    if all_filled:
        st.success("All required fields look filled. Ready to generate PDF.")
    else:
        st.warning("Please fill all fields and upload a valid photo (≤ 1 MB).")

    if st.button("Generate Resume PDF", disabled=(not all_filled)):
        photo_bytes = None
        if photo_file:
            photo_bytes = photo_file.read()
        data = {
            "full_name": full_name.strip(),
            "phone": phone.strip(),
            "email": email.strip(),
            "city_state": city_state.strip(),
            "summary": summary.strip(),
            "degree": degree.strip(),
            "institution": institution.strip(),
            "graduation_date": graduation_date.strip(),
            "license_number": license_number.strip(),
            "job_title": job_title.strip(),
            "duties": duties.strip(),
            "hard_skills": hard_skills.strip(),
            "soft_skills": soft_skills.strip(),
        }
        try:
            pdf_bytes = generate_pdf(data, photo_bytes)
            st.session_state['resume_pdf_bytes'] = pdf_bytes
            st.success("PDF generated — click Download to save the resume.")
        except Exception as e:
            st.error(f"Failed to generate PDF: {e}")

    if st.session_state.get('resume_pdf_bytes'):
        fname = f"{full_name.strip().replace(' ', '_')}_Resume.pdf" if full_name else "resume.pdf"
        st.download_button(
            label="Download Resume PDF",
            data=st.session_state['resume_pdf_bytes'],
            file_name=fname,
            mime="application/pdf"
        )

with col2:
    st.header("Live Preview")
    st.markdown("#### " + (full_name if full_name else "Full Name"))
    st.write(f"**{job_title}**" if job_title else "")
    st.write(f"{city_state}")
    st.write(f"📞 {phone} | ✉️ {email}")
    st.markdown("**Professional Summary**")
    st.write(summary if summary else "Your professional summary will appear here.")
    st.markdown("**Education**")
    if degree or institution or graduation_date:
        st.write(f"{degree} — {institution} ({graduation_date})")
    else:
        st.write("Education info will appear here.")
