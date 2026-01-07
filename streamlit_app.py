import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF
import matplotlib.pyplot as plt
import io
import re

# 1. Professional Page Setup
st.set_page_config(page_title="CENT-S Engine", layout="wide")
st.title("🏛️ CENT-S Engine: Graphics & Logic Edition")

# 2. Secure API Connection
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# PERSISTENCE
if "exam_text" not in st.session_state:
    st.session_state.exam_text = None
if "pdf_data" not in st.session_state:
    st.session_state.pdf_data = None

def create_coordinate_plane():
    """Generates a professional coordinate graph buffer."""
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.axhline(0, color='black', linewidth=1.2)
    ax.axvline(0, color='black', linewidth=1.2)
    ax.grid(True, linestyle=':', alpha=0.7)
    ax.set_xticks(range(-5, 6))
    ax.set_yticks(range(-5, 6))
    ax.set_title("Cartesian Plane Reference", fontsize=10)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf

# 3. File Upload
uploaded_file = st.file_uploader("Upload reference CENT-S material (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    context_text = "".join([page.extract_text() for page in reader.pages[:10]])

    if st.button("Generate Official Exam with Schemas"):
        with st.spinner("Engineering 55 questions and drawing visuals..."):
            prompt = f"""
            Act as an Italian University Exam Designer. Generate a 55-question CENT-S Exam.
            DISTRIBUTION: 15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Physics.
            
            FORMATTING RULES:
            - Use Unicode for math: π, ², ³, ±, √, →.
            - NO complex LaTeX like \\frac. Use / instead.
            - Number 1-55. Options A), B), C), D) on separate lines.
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
            
            try:
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf")
                pdf.set_font("DejaVu", size=10)
            except:
                pdf.set_font("Helvetica", size=10)
            
            pdf.cell(0, 10, "CENT-S OFFICIAL PRACTICE TEST", ln=True, align='C')
            
            # --- Add Initial Cartesian Graph ---
            graph_buf = create_coordinate_plane()
            pdf.image(graph_buf, x=110, y=25, w=85) # Placed on the right side
            pdf.ln(10)

            lines = st.session_state.exam_text.splitlines()
            for line in lines:
                if not line.strip():
                    pdf.ln(2)
                    continue
                
                # Section Headers with Dividers
                if any(sect in line.upper() for sect in ["MATH", "REASONING", "BIOLOGY", "CHEMISTRY", "PHYSICS"]):
                    pdf.ln(5)
                    pdf.set_draw_color(200, 200, 200)
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(2)
                    pdf.multi_cell(180, 8, text=line.strip().upper())
                # Indented Options
                elif re.match(r'^[A-D]\)', line.strip()):
                    pdf.set_x(25) 
                    pdf.multi_cell(160, 7, text=line.strip())
                else:
                    # Question Text
                    pdf.multi_cell(180, 7, text=line.strip())

            # --- Add Geometric Triangle Schema at the End ---
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y() + 10
            pdf.set_draw_color(100, 100, 100)
            pdf.line(40, y+30, 100, y+30) # Base
            pdf.line(40, y+30, 70, y)      # Side AC
            pdf.line(70, y, 100, y+30)     # Side BC
            pdf.text(68, y-3, "C"); pdf.text(37, y+35, "A"); pdf.text(98, y+35, "B")
            pdf.set_font("DejaVu", size=9)
            pdf.text(110, y+15, "Figure 2: Geometric reference for Mathematics section")

            st.session_state.pdf_data = bytes(pdf.output())

# 4. Results
if st.session_state.exam_text:
    st.markdown("---")
    st.write(st.session_state.exam_text)
    if st.session_state.pdf_data:
        st.download_button("📥 Download Official PDF with Graphics", st.session_state.pdf_data, "CENTS_Exam.pdf")
