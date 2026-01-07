import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF

# 1. UI & Page Configuration
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
            Act as an Italian University Exam Designer. Generate a 55-question CENT-S Exam.
            
            FORMATTING RULES:
            1. Every question MUST have 4 options: A), B), C), D) on new lines.
            2. Use LaTeX for math (e.g., $x^2 + 4x + 4 = 0$).
            3. CRITICAL: Add spaces between ALL symbols in formulas to allow wrapping.
            
            Distribution: 15 Math, 15 Reason, 10 Bio, 10 Chem, 5 Phys.
            Reference: {context_text[:3000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- PROFESSIONAL PDF GENERATION ---
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=10)
            
            # Safety Wrapper: Forces a line break if text is too wide
            def safe_draw(pdf, text):
                lines = text.splitlines()
                for line in lines:
                    if not line.strip():
                        pdf.ln(4)
                        continue
                    
                    # We set a fixed width of 170mm (A4 is 210mm)
                    # This ensures the engine NEVER runs out of horizontal space.
                    pdf.multi_cell(w=170, h=7, text=line, align='L')

            # Render Exam
            safe_draw(pdf, st.session_state.exam_text)

            # DRAW GEOMETRY SCHEMA (Triangle)
            if pdf.get_y() > 230: pdf.add_page()
            y = pdf.get_y() + 10
            pdf.set_draw_color(0, 0, 0)
            pdf.line(20, y+30, 80, y+30) # Base
            pdf.line(20, y+30, 50, y)    # Left
            pdf.line(50, y, 80, y+30)    # Right
            pdf.set_font("Helvetica", "B", 10)
            pdf.text(48, y-2, "C")
            pdf.text(18, y+35, "A")
            pdf.text(78, y+35, "B")
            pdf.set_font("Helvetica", "I", 8)
            pdf.text(90, y+15, "Figure 1: Geometric reference for Math Section")

            st.session_state.pdf_data = bytes(pdf.output())

# 4. Results Section
if st.session_state.exam_text:
    st.markdown("---")
    st.markdown("### 📋 Exam Preview")
    st.write(st.session_state.exam_text)
    
    if st.session_state.pdf_data:
        st.download_button("📥 Download Official Exam PDF", data=st.session_state.pdf_data, file_name="CENTS_Official_Exam.pdf")
