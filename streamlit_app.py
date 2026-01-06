import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF

# 1. Professional UI Setup
st.set_page_config(page_title="CENT-S Engine", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
    h1 { font-family: 'Playfair Display', serif; text-align: center; color: #1a1a1a; }
    [data-testid="stSidebar"] {display: none;}
    .stButton>button { border-radius: 20px; width: 100%; height: 3.5em; font-weight: bold; background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Official CENT-S Scientific Exam")

# 2. Secure API Connection
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# PERSISTENCE: Keep data alive across reruns
if "exam_text" not in st.session_state:
    st.session_state.exam_text = None
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

# 3. Reference Material Upload
uploaded_file = st.file_uploader("Upload reference CENT-S material (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    context_text = "".join([page.extract_text() for page in reader.pages[:10]])

    if st.button("Generate Full 55-Question Exam"):
        with st.spinner("Engineering 55 scientific questions... This may take a minute."):
            # Re-emphasized counts to prevent the AI from stopping at 45
            prompt = f"""
            Act as a CISIA Exam Designer. Create a full CENT-S Scientific Exam.
            YOU MUST PROVIDE EXACTLY 55 QUESTIONS TOTAL. 
            
            REQUIRED DISTRIBUTION:
            - Mathematics: 15 questions (numbered 1-15)
            - Reasoning on Texts and Data: 15 questions (numbered 16-30)
            - Biology: 10 questions (numbered 31-40)
            - Chemistry: 10 questions (numbered 41-50)
            - Physics: 5 questions (numbered 51-55)
            
            STRICT RULES:
            1. Exactly 4 options (a, b, c, d) per question.
            2. RANDOMIZE the correct answer (ensure a balanced spread of a, b, c, and d).
            3. Provide an Answer Key at the very end.
            
            Reference: {context_text[:3000]}
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- PDF Generation with Byte Conversion ---
            pdf = FPDF()
            pdf.add_page()
            try:
                # Using the font file in your repo
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
                pdf.set_font("DejaVu", size=10)
            except:
                pdf.set_font("Helvetica", size=10)
            
            pdf.multi_cell(0, 10, txt=st.session_state.exam_text)
            
            # FIX: Convert bytearray to bytes for Streamlit
            st.session_state.pdf_bytes = bytes(pdf.output())

    # 4. Results & Download
    if st.session_state.exam_text and st.session_state.pdf_bytes:
        st.markdown("---")
        st.markdown(st.session_state.exam_text)

        st.download_button(
            label="📥 Download Official 55-Question PDF",
            data=st.session_state.pdf_bytes,
            file_name="CENT-S_Full_Exam.pdf",
            mime="application/pdf"
        )
