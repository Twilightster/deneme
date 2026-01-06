import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF
import io

# 1. Page Config & Styling
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

if uploaded_file:
    reader = PdfReader(uploaded_file)
    context = "".join([page.extract_text() for page in reader.pages[:10]])
    st.success("Syllabus logic analyzed.")

    if st.button("Generate Full 55-Question Exam"):
        with st.spinner("Engineering official exam structure..."):
            prompt = f"""
            Act as a CISIA Exam Designer. Create a full CENT-S Scientific Exam.
            
            DISTRIBUTION:
            - 15 Mathematics questions.
            - 15 Reasoning on Texts and Data.
            - 10 Biology questions.
            - 10 Chemistry questions.
            - 5 Physics questions.
            
            STRICT RULES:
            1. Exactly 4 options (a, b, c, d) per question.
            2. RANDOMIZE correct answers. Spread them evenly so they are not clustered at 'b' or 'c'.
            3. No 'Powered by Groq' or conversational text.
            4. Include an Answer Key at the very end.
            
            Reference Context: {context[:3000]}
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            exam_output = response.choices[0].message.content
            st.session_state.exam_text = exam_text = exam_output
            st.markdown(exam_text)

            # 4. Secure PDF Generation
            pdf = FPDF()
            pdf.add_page()
            
            # Use the font you uploaded to GitHub
            try:
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
                pdf.set_font("DejaVu", size=10)
            except:
                pdf.set_font("Helvetica", size=10)
            
            pdf.multi_cell(0, 10, txt=exam_text)
            pdf_data = pdf.output(dest='S')
            
            # The Download Button
            st.download_button(
                label="📥 Download Official Exam PDF",
                data=pdf_data,
                file_name="CENT-S_Final_Exam.pdf",
                mime="application/pdf"
            )
