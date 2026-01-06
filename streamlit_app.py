import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF
import io
import random

# Elegant Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap');
    h1, h2 { font-family: 'Playfair Display', serif; }
    [data-testid="stSidebar"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Official CENT-S Exam Generator")

# Secure API Key from Streamlit Secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

uploaded_file = st.file_uploader("Upload reference CENT-S material (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    context = "".join([page.extract_text() for page in reader.pages[:10]])
    st.success("Syllabus logic analyzed.")

    if st.button("Generate Full 55-Question Exam"):
        with st.spinner("Engineering 55 scientific questions..."):
            # Detailed Prompt to ensure standard distribution and answer spread
            prompt = f"""
            Act as a CISIA Exam Designer. Create a full CENT-S Exam based on this context: {context[:3000]}
            
            DISTRIBUTION:
            1. 15 Mathematics questions (Algebra, Trigonometry, Calculus).
            2. 15 Reasoning on Texts and Data.
            3. 10 Biology questions (Cell, Genetics, Anatomy).
            4. 10 Chemistry questions (Stoichiometry, Periodic Table).
            5. 5 Physics questions (Mechanics, Thermodynamics).
            
            STRICT RULES:
            - EXACTLY 4 options (a, b, c, d) per question.
            - RANDOMIZE the correct answer position. Spread 'a, b, c, d' evenly across the 55 questions.
            - Format: "Q[number]. [Question text]" followed by the options.
            - List all answers in a separate 'Answer Key' section at the very end.
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            full_exam = response.choices[0].message.content
            st.markdown(full_exam)

            # PDF Generation
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Times", size=12)
            pdf.multi_cell(0, 10, txt=full_exam)
            
            # Use BytesIO to create a downloadable file
            pdf_output = pdf.output(dest='S')
            st.download_button(
                label="📥 Download Official Exam PDF",
                data=pdf_output,
                file_name="CENT-S_Full_Exam.pdf",
                mime="application/pdf"
            )
