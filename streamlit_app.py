import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF
import io

# Elegant Layout & Hidden Branding
st.set_page_config(page_title="CENT-S Engine", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap');
    h1, h2 { font-family: 'Playfair Display', serif; }
    [data-testid="stSidebar"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Official CENT-S Scientific Exam")

# Secret Management
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add 'GROQ_API_KEY' to your Streamlit Secrets.")
    st.stop()

uploaded_file = st.file_uploader("Upload reference CENT-S material (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    context = "".join([page.extract_text() for page in reader.pages[:15]])
    st.success("Exam patterns and scientific syllabus analyzed.")

    if st.button("Generate Full 55-Question Paper"):
        with st.spinner("Compiling scientific sections..."):
            prompt = f"""
            Act as a CISIA Exam Designer. Generate a full CENT-S Scientific Exam.
            SYLLABUS DISTRIBUTION:
            1. 15 Mathematics questions.
            2. 15 Reasoning on Texts and Data.
            3. 10 Biology questions.
            4. 10 Chemistry questions.
            5. 5 Physics questions.
            
            STRICT RULES:
            - Exactly 4 options (a, b, c, d) per question.
            - SPREAD correct answers evenly across a, b, c, d. Do not cluster them.
            - Use a formal academic tone. No AI chatter or 'Powered by' text.
            - Answer Key must be at the very end.
            Context: {context[:4000]}
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            exam_text = response.choices[0].message.content
            st.markdown(exam_text)

            # Professional PDF Generation with Unicode Support
            pdf = FPDF()
            pdf.add_page()
            
            # --- CRITICAL: Add and set your custom font here ---
            # Make sure 'DejaVuSans.ttf' is uploaded to your GitHub repo!
            try:
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
                pdf.set_font("DejaVu", size=10)
            except:
                st.warning("Custom font file not found. Falling back to Helvetica (may cause errors with special symbols).")
                pdf.set_font("Helvetica", size=10)
            
            pdf.multi_cell(0, 10, txt=exam_text)
            
            pdf_output = pdf.output(dest='S')
            st.download_button(
                label="📥 Download Official Exam PDF",
                data=pdf_output,
                file_name="CENT-S_Scientific_Exam.pdf",
                mime="application/pdf"
            )
