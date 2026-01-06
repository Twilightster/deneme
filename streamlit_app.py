import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF
import io

# 1. Elegant Styling
st.set_page_config(page_title="CENT-S Engine", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
    h1 { font-family: 'Playfair Display', serif; text-align: center; }
    [data-testid="stSidebar"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ CENT-S Scientific Exam Generator")

# 2. API Connection
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# 3. File Upload
uploaded_file = st.file_uploader("Upload reference CENT-S material (PDF)", type="pdf")

# Use Session State to store the exam so it doesn't disappear
if "exam_text" not in st.session_state:
    st.session_state.exam_text = None

if uploaded_file:
    reader = PdfReader(uploaded_file)
    context = "".join([page.extract_text() for page in reader.pages[:10]])
    
    if st.button("Generate Full 55-Question Exam"):
        with st.spinner("Engineering official exam structure..."):
            prompt = f"Create a full 55-question CENT-S Scientific Exam (15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Phys). Randomize answer positions. Context: {context[:3000]}"
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content

    # 4. Display and Download (Only if exam exists)
    if st.session_state.exam_text:
        st.markdown("---")
        st.markdown(st.session_state.exam_text)

        # Generate PDF in memory
        pdf = FPDF()
        pdf.add_page()
        try:
            pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
            pdf.set_font("DejaVu", size=10)
        except:
            pdf.set_font("Helvetica", size=10)
        
        pdf.multi_cell(0, 10, txt=st.session_state.exam_text)
        
        # This destination 'S' returns the PDF as a string/byte string
        pdf_bytes = pdf.output(dest='S').encode('latin-1') 
        
        st.download_button(
            label="📥 Download Official Exam PDF",
            data=pdf_bytes,
            file_name="CENT-S_Final_Exam.pdf",
            mime="application/pdf"
        )
