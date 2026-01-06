import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF
import io

# 1. Page Configuration & Professional Styling
st.set_page_config(page_title="CENT-S Engine", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
    h1 { font-family: 'Playfair Display', serif; text-align: center; color: #1a1a1a; }
    [data-testid="stSidebar"] {display: none;}
    .stButton>button { border-radius: 20px; width: 100%; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Official CENT-S Scientific Exam")

# 2. Secure API Connection
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# Initialize Session State to keep the exam alive across reruns
if "exam_result" not in st.session_state:
    st.session_state.exam_result = None

# 3. Reference Material Upload
uploaded_file = st.file_uploader("Upload reference CENT-S material (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    context_text = "".join([page.extract_text() for page in reader.pages[:10]])

    if st.button("Generate Full 55-Question Exam"):
        with st.spinner("Engineering official scientific exam structure..."):
            prompt = f"""
            Act as a CISIA Exam Designer. Generate a full CENT-S Scientific Exam.
            DISTRIBUTION: 15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Physics.
            STRICT RULES: 
            - Exactly 4 options (a, b, c, d). 
            - RANDOMIZE correct answer positions (spread them evenly).
            - Formal academic tone. 
            - Include an Answer Key at the very end.
            Context: {context_text[:3000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_result = response.choices[0].message.content

    # 4. Display and Download Section (Only if exam exists)
    if st.session_state.exam_result:
        st.markdown("---")
        st.markdown(st.session_state.exam_result)

        # Create PDF in-memory
        pdf = FPDF()
        pdf.add_page()
        
        try:
            # Using the font you successfully uploaded to GitHub (image_7a4d1d.png)
            pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
            pdf.set_font("DejaVu", size=10)
        except:
            pdf.set_font("Helvetica", size=10)
        
        pdf.multi_cell(0, 10, txt=st.session_state.exam_result)
        
        # We use a binary stream to ensure the download button gets valid data
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')
        
        st.download_button(
            label="📥 Download Official Exam PDF",
            data=pdf_bytes,
            file_name="CENT-S_Scientific_Exam.pdf",
            mime="application/pdf"
        )
