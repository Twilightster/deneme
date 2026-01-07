import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF

# 1. Professional Page Setup
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
        with st.spinner("Engineering 55 scientific questions..."):
            prompt = f"Generate 55 CENT-S questions (15 Math, 15 Reason, 10 Bio, 10 Chem, 5 Phys). Use simple LaTeX. NO TABLES. Context: {context_text[:2000]}"
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- CRASH-PROOF PDF GENERATION ---
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=25) # Increased margin for safety
            pdf.add_page()
            pdf.set_font("Helvetica", size=10) 
            
            lines = st.session_state.exam_text.splitlines()
            for line in lines:
                if not line.strip():
                    pdf.ln(5)
                    continue
                
                # TITANIUM FIX: If any line is longer than 55 characters, 
                # we force break it to guarantee it stays inside page margins.
                if len(line) > 55:
                    chunks = [line[i:i+55] for i in range(0, len(line), 55)]
                    for chunk in chunks:
                        # Use a width of 160mm to ensure it stays far from the edge
                        pdf.multi_cell(160, 8, text=chunk, align='L')
                else:
                    pdf.multi_cell(160, 8, text=line, align='L')
            
            st.session_state.pdf_data = bytes(pdf.output())

# 4. Results & Download (Preview is always shown)
if st.session_state.exam_text:
    st.markdown("---")
    st.markdown("### 📋 Generated Exam Preview")
    st.write(st.session_state.exam_text)
    
    if st.session_state.pdf_data:
        st.download_button(
            label="📥 Download Official Exam PDF",
            data=st.session_state.pdf_data,
            file_name="CENTS_Exam.pdf",
            mime="application/pdf"
        )
