import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF

# 1. Page Configuration
st.set_page_config(page_title="CENT-S Engine", layout="centered")
st.title("🏛️ CENT-S Engine")

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

    if st.button("Generate Full 55-Question Exam"):
        with st.spinner("Engineering 55 scientific questions..."):
            prompt = f"""
            Act as a CISIA Exam Designer. Generate a full 55-question CENT-S Scientific Exam.
            STRUCTURE: 15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Physics.
            RULES: Use simple LaTeX. NO TABLES. 4 options (a,b,c,d).
            Context: {context_text[:3000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- THE ULTIMATE SAFE PDF GENERATION ---
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Using the font file in your repo [cite: 702]
            try:
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf")
                pdf.set_font("DejaVu", size=10)
            except:
                pdf.set_font("Helvetica", size=10)
            
            # Split text and enforce character limits to prevent horizontal space errors 
            lines = st.session_state.exam_text.splitlines()
            for line in lines:
                # Sanitize: Remove characters that might break PDF width calculation
                clean_line = line.encode('utf-8', 'ignore').decode('utf-8')
                
                if len(clean_line) > 70:
                    # Force break long lines into safe 70-character chunks
                    for i in range(0, len(clean_line), 70):
                        pdf.multi_cell(0, 7, text=clean_line[i:i+70])
                elif clean_line.strip():
                    pdf.multi_cell(0, 7, text=clean_line)
                else:
                    pdf.ln(3)
            
            st.session_state.pdf_data = bytes(pdf.output())

if st.session_state.exam_text and st.session_state.pdf_data:
    st.markdown("---")
    st.markdown(st.session_state.exam_text)
    st.download_button(
        label="📥 Download Full 55-Question Exam",
        data=st.session_state.pdf_data,
        file_name="CENTS_Full_Exam.pdf",
        mime="application/pdf"
    )
