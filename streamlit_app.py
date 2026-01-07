import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF
import re

# 1. Page Configuration
st.set_page_config(page_title="CENT-S Engine", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
    h1 { font-family: 'Playfair Display', serif; text-align: center; color: #1a1a1a; }
    [data-testid="stSidebar"] {display: none;}
    .stButton>button { border-radius: 20px; width: 100%; height: 3.5em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ CENT-S Engine")

# 2. API Connection
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# PERSISTENCE
if "exam_text" not in st.session_state:
    st.session_state.exam_text = None
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

# 3. Reference Material Upload
uploaded_file = st.file_uploader("Upload reference CENT-S material (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    context_text = "".join([page.extract_text() for page in reader.pages[:15]])

    if st.button("Generate Pro 55-Question Exam"):
        with st.spinner("Engineering 110-minute scientific structure with LaTeX and Tables..."):
            prompt = f"""
            Act as a CISIA Exam Designer. Generate a full 55-question CENT-S Scientific Exam.
            
            DISTRIBUTION:
            - 15 Math (Q 1-15)
            - 15 Reasoning (Q 16-30) - INCLUDE AT LEAST 2 DATA TABLES.
            - 10 Biology (Q 31-40)
            - 10 Chemistry (Q 41-50)
            - 5 Physics (Q 51-55)
            
            FORMATTING RULES:
            1. Use LaTeX for all math/science (e.g., $\int_{{0}}^{{x}}$ or $CaCO_{{3}}$).
            2. For Reasoning tables, use Markdown format: | Col 1 | Col 2 |
            3. Exactly 4 options (a, b, c, d). Randomize correct answers.
            4. No conversational text. Answer Key at the very end.
            
            Context: {context_text[:4000]}
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- PDF Generation ---
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            try:
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf")
                pdf.set_font("DejaVu", size=10)
            except:
                pdf.set_font("Helvetica", size=10)

            # Split text to handle tables vs normal text
            lines = st.session_state.exam_text.split('\n')
            for line in lines:
                if "|" in line and "-" not in line: # Simple table detection
                    cols = [c.strip() for c in line.split("|") if c.strip()]
                    if cols:
                        with pdf.table() as table:
                            row = table.row()
                            for col in cols:
                                row.cell(col)
                else:
                    pdf.multi_cell(0, 8, txt=line)
            
            st.session_state.pdf_bytes = bytes(pdf.output())

    if st.session_state.exam_text and st.session_state.pdf_bytes:
        st.markdown("---")
        st.markdown(st.session_state.exam_text)

        st.download_button(
            label="📥 Download Pro Exam PDF",
            data=st.session_state.pdf_bytes,
            file_name="CENTS_Engine_Pro.pdf",
            mime="application/pdf"
        )
