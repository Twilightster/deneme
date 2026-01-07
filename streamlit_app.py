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

# PERSISTENCE: Data remains safe during reruns
if "exam_text" not in st.session_state:
    st.session_state.exam_text = None
if "pdf_data" not in st.session_state:
    st.session_state.pdf_data = None

# 3. Reference Material Upload
uploaded_file = st.file_uploader("Upload reference CENT-S material (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    # Analyze up to 15 pages for deeper syllabus context
    context_text = "".join([page.extract_text() for page in reader.pages[:15]])

    if st.button("Generate Full 55-Question Exam"):
        with st.spinner("Engineering official 55-question structure..."):
            prompt = f"""
            Act as a CISIA Exam Designer. Generate a full 55-question CENT-S Scientific Exam.
            
            STRUCTURE REQUIREMENTS:
            - Mathematics: 15 questions (numbered 1-15)
            - Reasoning on Texts and Data: 15 questions (numbered 16-30)
            - Biology: 10 questions (numbered 31-40)
            - Chemistry: 10 questions (numbered 41-50)
            - Physics: 5 questions (numbered 51-55)
            
            STRICT RULES:
            1. Use LaTeX for math/science (e.g., $log_{{2}}200$ or $CaCO_{{3}}$).
            2. For reasoning data, present it as a clear vertical list instead of a grid.
            3. Exactly 4 options (a, b, c, d). RANDOMIZE correct answers.
            4. Include a numbered Answer Key at the very end.
            
            Reference: {context_text[:4000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- Safe PDF Generation ---
            pdf = FPDF()
            pdf.add_page()
            try:
                # Use the font verified in your GitHub repository
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
                pdf.set_font("DejaVu", size=10)
            except:
                pdf.set_font("Helvetica", size=10)
            
            # Use multi_cell for all lines to prevent horizontal space errors
            lines = st.session_state.exam_text.split('\n')
            for line in lines:
                if line.strip():
                    # Width=0 means use the full width of the page margin to margin
                    pdf.multi_cell(0, 8, txt=line)
                else:
                    pdf.ln(4)
            
            # Convert to bytes for safe Streamlit downloading
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
