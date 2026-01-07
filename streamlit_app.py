import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF
import re

# 1. Professional UI Setup
st.set_page_config(page_title="CENT-S Engine", layout="wide")
st.title("🏛️ CENT-S Engine: Official Edition")

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

    if st.button("Generate Official Exam"):
        with st.spinner("Engineering high-fidelity exam and schemas..."):
            prompt = f"""
            Act as an Italian University Exam Designer. Generate a 55-question practice CENT-S Exam.
            DISTRIBUTION: 15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Physics.
            
            STRICT FORMATTING RULES:
            - Number questions 1 to 55.
            - Every question MUST follow this EXACT pattern:
              [Question Text]
              A) [Option]
              B) [Option]
              C) [Option]
              D) [Option]
            - Use LaTeX for ALL math/science (e.g., $x^2 + 4x + 4 = 0$).
            - Place the Answer Key at the very end.
            Reference: {context_text[:3000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- STRUCTURED PDF GENERATION ---
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=20)
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "CENT-S OFFICIAL PRACTICE TEST", ln=True, align='C')
            pdf.set_font("Helvetica", "", 10)
            pdf.ln(5)

            lines = st.session_state.exam_text.splitlines()
            for line in lines:
                if not line.strip():
                    pdf.ln(2)
                    continue
                
                # Detect Options and apply indentation for clean look
                if re.match(r'^[A-D]\)', line.strip()):
                    pdf.set_x(20) # Indent options
                    pdf.multi_cell(170, 7, text=line.strip())
                elif any(sect in line.upper() for sect in ["MATH", "REASONING", "BIOLOGY", "CHEMISTRY", "PHYSICS"]):
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.ln(5)
                    pdf.multi_cell(180, 8, text=line.strip())
                    pdf.set_font("Helvetica", "", 10)
                else:
                    # General text wrapping with safety width to prevent horizontal space error
                    pdf.multi_cell(180, 7, text=line.strip())

            # ATTACH GEOMETRIC SCHEMA
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y() + 10
            pdf.set_draw_color(0, 0, 0)
            pdf.line(30, y+30, 90, y+30) # Base
            pdf.line(30, y+30, 60, y)    # Left
            pdf.line(60, y, 90, y+30)    # Right
            pdf.set_font("Helvetica", "B", 10)
            pdf.text(58, y-2, "C")
            pdf.text(28, y+35, "A")
            pdf.text(88, y+35, "B")
            pdf.set_font("Helvetica", "I", 8)
            pdf.text(100, y+15, "Figure 1: Geometric reference for Mathematics section")

            st.session_state.pdf_data = bytes(pdf.output())

# 4. Results Section
if st.session_state.exam_text:
    st.markdown("---")
    st.markdown(st.session_state.exam_text)
    
    if st.session_state.pdf_data:
        st.download_button(
            label="📥 Download Structured Exam PDF",
            data=st.session_state.pdf_data,
            file_name="CENTS_Official_Exam.pdf",
            mime="application/pdf"
        )
