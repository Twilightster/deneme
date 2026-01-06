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

# PERSISTENCE: This part prevents the 'vanishing' data error
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
        with st.spinner("Engineering 110-minute scientific structure..."):
            prompt = f"""
            Act as a CISIA Exam Designer. Create a full CENT-S Scientific Exam.
            STRUCTURE: 15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Physics.
            STRICT RULES: 
            1. Exactly 4 options (a, b, c, d) per question. 
            2. RANDOMIZE correct answer positions (spread them evenly).
            3. No conversational text. Answer Key at the very end.
            Reference Context: {context_text[:3000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            # Store the text result
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- Build and Store the PDF Bytes immediately ---
            pdf = FPDF()
            pdf.add_page()
            try:
                # Using the font file in your repo (image_7a4d1d.png)
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
                pdf.set_font("DejaVu", size=10)
            except:
                pdf.set_font("Helvetica", size=10)
            
            pdf.multi_cell(0, 10, txt=st.session_state.exam_text)
            
            # Save the binary data so it survives the button-click rerun
            st.session_state.pdf_bytes = pdf.output()

    # 4. Display and Download Logic
    if st.session_state.exam_text and st.session_state.pdf_bytes:
        st.markdown("---")
        st.markdown(st.session_state.exam_text)

        # The data is now safely pulled from st.session_state
        st.download_button(
            label="📥 Download Official Exam PDF",
            data=st.session_state.pdf_bytes,
            file_name="CENT-S_Scientific_Exam.pdf",
            mime="application/pdf"
        )
