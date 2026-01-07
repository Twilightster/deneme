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

    if st.button("Generate Professional Exam"):
        with st.spinner("Engineering high-fidelity exam with Unicode support..."):
            prompt = f"""
            Act as an Italian University Exam Designer. Generate a 55-question practice CENT-S Exam.
            DISTRIBUTION: 15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Physics.
            
            READABILITY RULES:
            - Use standard Unicode symbols: π, ², ³, ±, √, →.
            - NO complex LaTeX code like \\frac. Use / instead.
            - Format: Question number, Question text, then A), B), C), D) on separate lines.
            - Ensure there are spaces between math symbols to allow clean wrapping.
            Reference: {context_text[:3000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- STRUCTURED UNICODE PDF GENERATION ---
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=20)
            pdf.add_page()
            
            # Use DejaVuSans for Unicode support (pi, squared, etc.)
            try:
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf")
                pdf.set_font("DejaVu", size=10)
            except:
                pdf.set_font("Helvetica", size=10)
            
            # Title Header
            pdf.cell(0, 12, "CENT-S OFFICIAL PRACTICE TEST", ln=True, align='C')
            pdf.ln(5)

            lines = st.session_state.exam_text.splitlines()
            for line in lines:
                if not line.strip():
                    pdf.ln(2)
                    continue
                
                # Detect Section Headers
                if any(sect in line.upper() for sect in ["MATH", "REASONING", "BIOLOGY", "CHEMISTRY", "PHYSICS"]):
                    pdf.ln(5)
                    pdf.multi_cell(180, 8, text=line.strip().upper())
                # Detect and Indent Options A, B, C, D
                elif re.match(r'^[A-D]\)', line.strip()):
                    pdf.set_x(25) 
                    pdf.multi_cell(160, 7, text=line.strip())
                else:
                    # Normal Question wrapping (Safety width 180mm)
                    pdf.multi_cell(180, 7, text=line.strip())

            # ADD THE TRIANGLE SCHEMA
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y() + 10
            pdf.set_draw_color(150, 150, 150)
            pdf.line(40, y+30, 100, y+30) # Base AB
            pdf.line(40, y+30, 70, y)      # Side AC
            pdf.line(70, y, 100, y+30)     # Side BC
            pdf.text(68, y-3, "C")
            pdf.text(37, y+35, "A")
            pdf.text(98, y+35, "B")
            pdf.set_font("DejaVu", size=9)
            pdf.text(110, y+15, "Figure 1: Geometric reference")

            st.session_state.pdf_data = bytes(pdf.output())

# 4. Results Section
if st.session_state.exam_text:
    st.markdown("---")
    st.write(st.session_state.exam_text)
    
    if st.session_state.pdf_data:
        st.download_button(
            label="📥 Download Clean Unicode Exam PDF",
            data=st.session_state.pdf_data,
            file_name="CENTS_Official_Exam.pdf",
            mime="application/pdf"
        )
