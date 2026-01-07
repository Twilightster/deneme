import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF

# 1. Page Configuration
st.set_page_config(page_title="CENT-S Engine", layout="centered")
st.title("🏛️ CENT-S Engine")

# 2. Secure API Connection
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# PERSISTENCE
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
        with st.spinner("Engineering questions..."):
            prompt = f"Generate 55 CENT-S questions (15 Math, 15 Reason, 10 Bio, 10 Chem, 5 Phys). Use simple text only. Ensure no extremely long unbroken words or formulas. Context: {context_text[:2000]}"
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- THE ULTIMATE SAFE PDF GENERATION ---
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=20)
            pdf.add_page()
            # Using Helvetica for maximum stability across all characters
            pdf.set_font("Helvetica", size=10) 
            
            def safe_text_output(pdf, text, max_chars=60):
                """Force-breaks any line longer than max_chars to prevent horizontal space errors."""
                lines = text.splitlines()
                for line in lines:
                    if not line.strip():
                        pdf.ln(5)
                        continue
                    
                    # If a line is physically too long, chop it into chunks
                    if len(line) > max_chars:
                        for i in range(0, len(line), max_chars):
                            chunk = line[i:i+max_chars]
                            pdf.multi_cell(0, 8, text=chunk)
                    else:
                        pdf.multi_cell(0, 8, text=line)

            # Process the generated text through the safe wrapper
            safe_text_output(pdf, st.session_state.exam_text)
            
            # Convert to bytes for safe Streamlit download [cite: 91, 715, 822]
            st.session_state.pdf_data = bytes(pdf.output())

# 4. Results & Download (Always show preview if data exists)
if st.session_state.exam_text:
    st.markdown("---")
    st.markdown("### 📋 Exam Preview")
    st.info("Your questions are generated below. If the PDF button crashes, copy directly from here.")
    st.write(st.session_state.exam_text)
    
    if st.session_state.pdf_data:
        st.download_button(
            label="📥 Download Official Exam PDF",
            data=st.session_state.pdf_data,
            file_name="CENTS_Full_Exam.pdf",
            mime="application/pdf"
        )
