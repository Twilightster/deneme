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

    if st.button("Generate Official 55-Question Exam"):
        with st.spinner("Engineering high-fidelity exam and clean formatting..."):
            prompt = f"""
            Act as an Italian University Exam Designer. Generate a 55-question practice CENT-S Exam.
            DISTRIBUTION: 15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Physics.
            
            STRICT RULES for READABILITY:
            - NO complex LaTeX code like \\frac or \\cup. 
            - Use simple text symbols: ^ for powers, / for fractions, * for multiplication.
            - Format: Question number, Question text, then A), B), C), D) on separate lines.
            - Every question MUST have 4 options.
            Reference: {context_text[:3000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            # Clean the text: remove all stray $ symbols and backslashes for PDF readability
            raw_text = response.choices[0].message.content
            st.session_state.exam_text = raw_text.replace('$', '').replace('\\', '')
            
            # --- STRUCTURED PDF GENERATION ---
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=20)
            pdf.add_page()
            
            # Title Header
            pdf.set_fill_color(245, 245, 245)
            pdf.rect(10, 10, 190, 15, 'F')
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 12, "CENT-S OFFICIAL PRACTICE TEST", ln=True, align='C')
            pdf.ln(5)

            lines = st.session_state.exam_text.splitlines()
            for line in lines:
                if not line.strip():
                    pdf.ln(2)
                    continue
                
                # Detect and Format Sections
                if any(sect in line.upper() for sect in ["MATH", "REASONING", "BIOLOGY", "CHEMISTRY", "PHYSICS"]):
                    pdf.set_font("Helvetica", "B", 12)
                    pdf.set_text_color(40, 40, 40)
                    pdf.ln(5)
                    pdf.multi_cell(180, 8, text=line.strip().upper())
                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(0, 0, 0)
                # Detect and Indent Options
                elif re.match(r'^[A-D]\)', line.strip()):
                    pdf.set_x(25) 
                    pdf.multi_cell(165, 7, text=line.strip())
                else:
                    # Question text formatting
                    pdf.multi_cell(180, 7, text=line.strip())

            # ADD THE TRIANGLE SCHEMA AT THE END
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y() + 10
            pdf.set_draw_color(100, 100, 100)
            pdf.line(40, y+30, 100, y+30) # Base AB
            pdf.line(40, y+30, 70, y)      # Side AC
            pdf.line(70, y, 100, y+30)     # Side BC
            pdf.set_font("Helvetica", "B", 10)
            pdf.text(68, y-3, "C")
            pdf.text(37, y+35, "A")
            pdf.text(98, y+35, "B")
            pdf.set_font("Helvetica", "I", 9)
            pdf.text(110, y+15, "Figure 1: Geometric reference for Math section")

            st.session_state.pdf_data = bytes(pdf.output())

# 4. Results Section
if st.session_state.exam_text:
    st.markdown("---")
    st.write(st.session_state.exam_text)
    
    if st.session_state.pdf_data:
        st.download_button(
            label="📥 Download Clean Official Exam PDF",
            data=st.session_state.pdf_data,
            file_name="CENTS_Official_Exam.pdf",
            mime="application/pdf"
        )
