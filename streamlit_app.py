import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF

# 1. Page Configuration & Elegant Style
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

# PERSISTENCE: Lock the data into session state
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
        with st.spinner("Engineering official 55-question structure..."):
            # Reinforced prompt to ensure exactly 55 questions
            prompt = f"""
            Act as a CISIA Exam Designer. Generate a full 55-question CENT-S Scientific Exam.
            YOU MUST GENERATE EXACTLY THIS MANY QUESTIONS PER SECTION:
            1. 15 Mathematics questions.
            2. 15 Reasoning on Texts and Data questions.
            3. 10 Biology questions.
            4. 10 Chemistry questions.
            5. 5 Physics questions.
            
            TOTAL: 55 QUESTIONS.
            
            RULES: 
            - Exactly 4 options (a, b, c, d) per question. 
            - RANDOMIZE correct answer positions (spread them evenly across a, b, c, d).
            - No conversational text. Answer Key at the very end.
            Context: {context_text[:3000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- Generate the PDF immediately and store it ---
            pdf = FPDF()
            pdf.add_page()
            try:
                # Using the font file confirmed in image_7a4d1d.png
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
                pdf.set_font("DejaVu", size=10)
            except:
                pdf.set_font("Helvetica", size=10)
            
            pdf.multi_cell(0, 10, txt=st.session_state.exam_text)
            st.session_state.pdf_data = pdf.output()

    # 4. Results & Download Section
    if st.session_state.exam_text and st.session_state.pdf_data:
        st.markdown("---")
        st.markdown(st.session_state.exam_text)

        st.download_button(
            label="📥 Download Official 55-Question PDF",
            data=st.session_state.pdf_data,
            file_name="CENT-S_Scientific_Full_Exam.pdf",
            mime="application/pdf"
        )
