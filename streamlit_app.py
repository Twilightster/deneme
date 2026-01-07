import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF

# 1. Page Configuration
st.set_page_config(page_title="CENT-S Engine", layout="wide")
st.title("🏛️ CENT-S Engine: Professional Edition")

# 2. Secure API Connection
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

if "exam_text" not in st.session_state:
    st.session_state.exam_text = None
if "pdf_data" not in st.session_state:
    st.session_state.pdf_data = None

uploaded_file = st.file_uploader("Upload reference CENT-S material (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    context_text = "".join([page.extract_text() for page in reader.pages[:10]])

    if st.button("Generate Official 55-Question Exam with Schemas"):
        with st.spinner("Engineering high-fidelity exam..."):
            prompt = f"""
            Act as an Italian University Exam Designer. Generate a 55-question CENT-S Exam.
            STRUCTURE: 15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Physics.
            
            STRICT FORMATTING:
            - Every question MUST have 4 options labeled A), B), C), D).
            - Use LaTeX for ALL math/science (e.g., $x^2 + 4x + 4 = 0$).
            - For Reasoning, include detailed data scenarios.
            Reference: {context_text[:3000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- PROFESSIONAL PDF GENERATION ---
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=20)
            pdf.add_page()
            
            # Draw a professional header box
            pdf.set_fill_color(240, 240, 240)
            pdf.rect(10, 10, 190, 20, 'F')
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "CENT-S OFFICIAL PRACTICE EXAM", ln=True, align='C')
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 10, "Time Allowed: 110 Minutes | 55 Questions", ln=True, align='C')
            pdf.ln(10)

            # Use Standard Helvetica for clean wrapping
            pdf.set_font("Helvetica", size=10)
            
            lines = st.session_state.exam_text.splitlines()
            for line in lines:
                if line.strip():
                    # Check for section headers to bold them
                    if any(sect in line.upper() for sect in ["MATH", "BIOLOGY", "CHEMISTRY", "PHYSICS", "REASONING"]):
                        pdf.set_font("Helvetica", "B", 12)
                        pdf.ln(5)
                        pdf.multi_cell(0, 10, text=line)
                        pdf.set_font("Helvetica", "", 10)
                    else:
                        # Professional Word-Wrapping (No character slicing)
                        pdf.multi_cell(0, 7, text=line)
                else:
                    pdf.ln(2)
            
            # Drawing a Sample Geometry Schema for the Math Section
            pdf.set_draw_color(0, 0, 0)
            pdf.line(20, 250, 60, 250) # Triangle Base
            pdf.line(20, 250, 40, 220) # Side A
            pdf.line(40, 220, 60, 250) # Side B
            pdf.text(38, 218, "C")

            st.session_state.pdf_data = bytes(pdf.output())

if st.session_state.exam_text:
    st.markdown("---")
    st.markdown(st.session_state.exam_text)
    
    if st.session_state.pdf_data:
        st.download_button("📥 Download Official Exam PDF", data=st.session_state.pdf_data, file_name="CENTS_Official_Exam.pdf")
