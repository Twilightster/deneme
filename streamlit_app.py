import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF
import textwrap

# 1. Page Configuration
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
        with st.spinner("Engineering high-fidelity exam and schemas..."):
            prompt = f"""
            Act as an Italian University Exam Designer. Generate a 55-question CENT-S Exam.
            DISTRIBUTION: 15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Physics.
            
            STRICT RULES:
            1. Every question MUST have 4 options labeled A), B), C), D) on new lines.
            2. Use LaTeX for math (e.g., $x^2 + 4x + 4 = 0$).
            3. Ensure ALL formulas have spaces between symbols to allow wrapping.
            4. Include an Answer Key at the end.
            Reference: {context_text[:3000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- PROFESSIONAL PDF GENERATION ---
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=25)
            pdf.add_page()
            pdf.set_font("Helvetica", size=10)
            
            # Draw Header
            pdf.set_fill_color(230, 230, 230)
            pdf.rect(10, 10, 190, 15, 'F')
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 12, "CENT-S OFFICIAL PRACTICE TEST", ln=True, align='C')
            pdf.ln(5)

            def smart_wrap(pdf, text, max_width=170):
                """Prevents 'Not enough horizontal space' by forcing breaks in long words."""
                lines = text.splitlines()
                for line in lines:
                    if not line.strip():
                        pdf.ln(4)
                        continue
                    
                    # Split into words to check for massive formulas
                    words = line.split(' ')
                    clean_line = ""
                    for word in words:
                        # If a single word/formula is > 50 chars, it will crash FPDF. 
                        # We force break it.
                        if len(word) > 50:
                            if clean_line: pdf.multi_cell(0, 7, text=clean_line)
                            pdf.multi_cell(0, 7, text=word[:45] + "-")
                            clean_line = word[45:] + " "
                        else:
                            clean_line += word + " "
                    
                    pdf.multi_cell(0, 7, text=clean_line)

            # Render text safely
            pdf.set_font("Helvetica", "", 10)
            smart_wrap(pdf, st.session_state.exam_text)

            # DRAW GEOMETRY SCHEMA (Triangle)
            if pdf.get_y() > 240: pdf.add_page() # Ensure space
            pdf.set_draw_color(50, 50, 50)
            y_start = pdf.get_y() + 10
            pdf.line(20, y_start + 30, 80, y_start + 30) # Base
            pdf.line(20, y_start + 30, 50, y_start)      # Left side
            pdf.line(50, y_start, 80, y_start + 30)      # Right side
            pdf.text(48, y_start - 2, "C")
            pdf.text(18, y_start + 34, "A")
            pdf.text(78, y_start + 34, "B")
            pdf.set_font("Helvetica", "I", 8)
            pdf.text(90, y_start + 15, "Figure 1: Triangle for Trigonometry Section")

            st.session_state.pdf_data = bytes(pdf.output())

# 4. Results Section
if st.session_state.exam_text:
    st.markdown("---")
    st.markdown("### 📋 Generated Exam Preview")
    st.write(st.session_state.exam_text)
    
    if st.session_state.pdf_data:
        st.download_button("📥 Download Official Exam PDF", data=st.session_state.pdf_data, file_name="CENTS_Official_Exam.pdf")
