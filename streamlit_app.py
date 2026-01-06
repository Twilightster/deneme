import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF

# 1. Professional Page Setup
st.set_page_config(page_title="CENT-S Engine", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
    h1 { font-family: 'Playfair Display', serif; text-align: center; color: #1a1a1a; }
    [data-testid="stSidebar"] {display: none;}
    .stButton>button { border-radius: 20px; width: 100%; height: 3.5em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Official CENT-S Scientific Exam")

# 2. Secure API Connection
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# PERSISTENCE: This part is critical to stop the error
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
        with st.spinner("Engineering official scientific exam structure..."):
            prompt = f"""
            Act as a CISIA Exam Designer. Generate a full CENT-S Scientific Exam.
            STRUCTURE: 15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Physics.
            STRICT RULES: Exactly 4 options (a, b, c, d). RANDOMIZE correct answers. 
            Formal academic tone. Include an Answer Key at the very end.
            Context: {context_text[:3000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            # Store results in session state so they survive the page rerun
            st.session_state.exam_text = response.choices[0].message.content
            
            # Create the PDF immediately after generation
            pdf = FPDF()
            pdf.add_page()
            try:
                # Using the font you successfully uploaded to GitHub (image_7a4d1d.png)
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
                pdf.set_font("DejaVu", size=10)
            except:
                pdf.set_font("Helvetica", size=10)
            
            pdf.multi_cell(0, 10, txt=st.session_state.exam_text)
            st.session_state.pdf_data = pdf.output()

    # 4. Display and Download (only if data exists)
    if st.session_state.exam_text and st.session_state.pdf_data:
        st.markdown("---")
        st.markdown(st.session_state.exam_text)

        st.download_button(
            label="📥 Download Official Exam PDF",
            data=st.session_state.pdf_data,
            file_name="CENT-S_Scientific_Exam.pdf",
            mime="application/pdf"
        )
