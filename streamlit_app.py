import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF
import io

# 1. Page Configuration & Elegant Style
st.set_page_config(page_title="CENT-S Engine", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
    h1 { font-family: 'Playfair Display', serif; text-align: center; color: #1a1a1a; }
    [data-testid="stSidebar"] {display: none;}
    .stButton>button { border-radius: 20px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Official CENT-S Scientific Exam")

# 2. Secure API Connection
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# Initialize Session State
if "final_exam" not in st.session_state:
    st.session_state.final_exam = None

# 3. File Upload & Analysis
uploaded_file = st.file_uploader("Upload reference CENT-S material (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    context = "".join([page.extract_text() for page in reader.pages[:10]])

    if st.button("Generate Full 55-Question Exam"):
        with st.spinner("Engineering official 110-minute exam structure..."):
            prompt = f"""
            Act as a CISIA Exam Designer. Generate a full CENT-S Scientific Exam.
            STRUCTURE:
            - 15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Physics.
            STRICT RULES:
            1. Exactly 4 options (a, b, c, d) per question.
            2. RANDOMIZE the correct answer positions (spread across a,b,c,d).
            3. Use formal academic tone. Answer Key at the very end.
            Context: {context[:3000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.final_exam = response.choices[0].message.content

    # 4. Display and Download Section
    if st.session_state.final_exam:
        st.markdown("---")
        st.markdown(st.session_state.final_exam)

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Using the font you successfully uploaded to GitHub
        try:
            pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
            pdf.set_font("DejaVu", size=10)
        except:
            st.warning("Font loading issue. Falling back to standard font.")
            pdf.set_font("Helvetica", size=10)
        
        pdf.multi_cell(0, 10, txt=st.session_state.final_exam)
        
        # FIX: Handle the output correctly as bytes for st.download_button
        pdf_bytes = pdf.output() 
        
        st.download_button(
            label="📥 Download Official Exam PDF",
            data=pdf_bytes,
            file_name="CENT-S_Scientific_Exam.pdf",
            mime="application/pdf"
        )
