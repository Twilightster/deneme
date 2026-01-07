import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF

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

# 3. Reference Material Upload
uploaded_file = st.file_uploader("Upload reference CENT-S material (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    context_text = "".join([page.extract_text() for page in reader.pages[:10]])

    if st.button("Generate Full 55-Question Exam"):
        with st.spinner("Engineering 55 scientific questions..."):
            prompt = f"""
            Act as a CISIA Exam Designer. Generate a full 55-question CENT-S Scientific Exam.
            STRUCTURE: 15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Physics.
            
            STRICT RULES:
            1. Use simple LaTeX ($...$). AVOID extremely long formulas on a single line.
            2. NO TABLES. Use bullet points for data sets.
            3. Exactly 4 options (a, b, c, d).
            4. Include an Answer Key at the very end.
            Reference: {context_text[:3000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- CRASH-PROOF PDF GENERATION ---
            pdf = FPDF()
            pdf.add_page()
            try:
                # Using the verified font in your repo
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf")
                pdf.set_font("DejaVu", size=10)
            except:
                pdf.set_font("Helvetica", size=10)
            
            lines = st.session_state.exam_text.splitlines()
            for line in lines:
                if line.strip():
                    # THE FIX: If a line is longer than 85 chars, force-break it 
                    # This prevents the 'Not enough horizontal space' crash.
                    if len(line) > 85:
                        chunks = [line[i:i+85] for i in range(0, len(line), 85)]
                        for chunk in chunks:
                            pdf.multi_cell(0, 7, text=chunk)
                    else:
                        pdf.multi_cell(0, 7, text=line)
                else:
                    pdf.ln(3)
            
            st.session_state.pdf_data = bytes(pdf.output())

    # 4. Results & Download
    if st.session_state.exam_text and st.session_state.pdf_data:
        st.markdown("---")
        st.markdown(st.session_state.exam_text)

        st.download_button(
            label="📥 Download Pro 55-Question PDF",
            data=st.session_state.pdf_data,
            file_name="CENTS_Full_Exam.pdf",
            mime="application/pdf"
        )
