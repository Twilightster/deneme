import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF
import io

# Elegant Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap');
    h1, h2 { font-family: 'Playfair Display', serif; }
    [data-testid="stSidebar"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Official CENT-S Exam Generator")

# Helper to fix Unicode errors
def clean_text(text):
    """Replaces smart quotes and other non-latin1 characters."""
    return text.encode('latin-1', 'replace').decode('latin-1').replace('?', "'")

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
            prompt = f"""
            Act as a CISIA Exam Designer. Create a full CENT-S Exam.
            STRUCTURE:
            - 15 Math questions.
            - 15 Reasoning on Texts and Data.
            - 10 Biology questions.
            - 10 Chemistry questions.
            - 5 Physics questions.
            
            RULES:
            1. Exactly 4 options (a, b, c, d).
            2. Spread correct answers EVENLY across a, b, c, and d. Do NOT cluster them.
            3. Use formal scientific English.
            4. Provide an Answer Key at the very end.
            Context: {context[:3000]}
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            raw_exam = response.choices[0].message.content
            
            # Sanitize text for PDF encoding
            safe_exam = clean_text(raw_exam)
            st.markdown(safe_exam)

            # PDF Generation
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(0, 10, txt=safe_exam)
            
            pdf_output = pdf.output(dest='S')
            st.download_button(
                label="📥 Download Official Exam PDF",
                data=pdf_output,
                file_name="CENT-S_Scientific_Exam.pdf",
                mime="application/pdf"
            )
