import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
import io
import re

# 1. Page Configuration
st.set_page_config(page_title="CENT-S Engine", layout="wide")
st.title("🏛️ CENT-S Engine: Official High-Fidelity Edition")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- GRAPHICS GENERATORS ---
def create_math_graph():
    """Generates a professional function graph for Question #1."""
    fig, ax = plt.subplots(figsize=(5, 3))
    x = np.linspace(-2, 4, 100)
    ax.plot(x, x**2 - 2*x, label="f(x) = x² - 2x", color='red', linewidth=1.5)
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(prop={'size': 8})
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

def draw_triangle_schema(pdf, y_pos):
    """Draws a professional vector triangle at a specific Y position."""
    pdf.set_draw_color(100, 100, 100)
    pdf.line(40, y_pos + 30, 100, y_pos + 30) # Base AB
    pdf.line(40, y_pos + 30, 70, y_pos)      # Side AC
    pdf.line(70, y_pos, 100, y_pos + 30)     # Side BC
    pdf.set_font("DejaVu", size=10)
    pdf.text(68, y_pos - 3, "C")
    pdf.text(37, y_pos + 35, "A")
    pdf.text(98, y_pos + 35, "B")
    return y_pos + 45

# 2. Persistence
if "exam_text" not in st.session_state: st.session_state.exam_text = None
if "pdf_data" not in st.session_state: st.session_state.pdf_data = None

# 3. File Upload & Processing
uploaded_file = st.file_uploader("Upload reference CENT-S material (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    context_text = "".join([page.extract_text() for page in reader.pages[:10]])

    if st.button("Generate Official 55-Question Exam"):
        with st.spinner("Engineering high-fidelity exam and dynamic graphics..."):
            prompt = f"""
            Act as a CISIA Exam Designer. Generate a 55-question practice CENT-S Exam.
            STRUCTURE: 15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Physics.
            
            RULES:
            - Question #1 MUST refer to the 'Function Graph' provided below.
            - Question #5 MUST refer to the 'Triangle Schema' provided below.
            - Use Unicode: π, ², ³, √, →. NO complex LaTeX.
            - Options A), B), C), D) on separate lines.
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
            pdf.ln(5)

            lines = st.session_state.exam_text.splitlines()
            for line in lines:
                if not line.strip(): continue
                
                # COLLISION FIX: Check for Question 1 and insert Graph
                if "1." in line[:3] and pdf.page_no() == 1:
                    pdf.multi_cell(180, 7, text=line.strip())
                    pdf.ln(2)
                    pdf.image(create_math_graph(), x=30, y=pdf.get_y(), w=140)
                    pdf.set_y(pdf.get_y() + 75)
                    continue

                # COLLISION FIX: Check for Question 5 and insert Triangle
                if "5." in line[:3]:
                    pdf.multi_cell(180, 7, text=line.strip())
                    pdf.ln(5)
                    new_y = draw_triangle_schema(pdf, pdf.get_y())
                    pdf.set_y(new_y)
                    continue

                # Section Dividers
                if any(sect in line.upper() for sect in ["MATH", "REASONING", "BIOLOGY", "CHEMISTRY", "PHYSICS"]):
                    pdf.ln(8)
                    pdf.set_draw_color(200, 200, 200)
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(2)
                    pdf.multi_cell(180, 8, text=line.strip().upper())
                # Indented Choice Grid
                elif re.match(r'^[A-D]\)', line.strip()):
                    pdf.set_x(25) 
                    pdf.multi_cell(160, 7, text=line.strip())
                else:
                    # Normal Text Safety Wrapper
                    pdf.multi_cell(180, 7, text=line.strip())

            st.session_state.pdf_data = bytes(pdf.output())

# 4. Results & Download
if st.session_state.exam_text:
    st.write(st.session_state.exam_text)
    if st.session_state.pdf_data:
        st.download_button("📥 Download Official CEnT-S PDF", st.session_state.pdf_data, "CEnT-S_Official_Practice.pdf")
