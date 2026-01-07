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

# 3. File Upload
uploaded_file = st.file_uploader("Upload reference CENT-S material (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    context_text = "".join([page.extract_text() for page in reader.pages[:10]])

    if st.button("Generate Full 55-Question Exam"):
        with st.spinner("Engineering questions..."):
            # We strictly tell the AI to use spaces to help with wrapping
            prompt = f"Generate 55 CENT-S questions (15 Math, 15 Reason, 10 Bio, 10 Chem, 5 Phys). Use simple text. Ensure math formulas have spaces around operators. Context: {context_text[:2000]}"
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- THE ULTIMATE SAFE PDF GENERATION ---
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=20)
            pdf.add_page()
            pdf.set_font("Helvetica", size=10) # Using standard font for maximum stability
            
            lines = st.session_state.exam_text.splitlines()
            for line in lines:
                if not line.strip():
                    pdf.ln(4)
                    continue
                
                # TITANIUM FIX: Manually slice the string into 50-character chunks
                # This makes it mathematically impossible to trigger a horizontal space error.
                chunk_size = 50
                chunks = [line[i:i+chunk_size] for i in range(0, len(line), chunk_size)]
                
                for chunk in chunks:
                    # 'text' instead of 'txt' to follow the latest library updates [cite: 702, 709]
                    pdf.multi_cell(w=0, h=8, text=chunk, align='L')
            
            st.session_state.pdf_data = bytes(pdf.output())

# 4. Results & Download (This will be visible even if PDF fails)
if st.session_state.exam_text:
    st.markdown("---")
    st.markdown("### 📋 Generated Exam Preview")
    st.info("If the download button below crashes, copy your questions directly from this preview.")
    st.write(st.session_state.exam_text)
    
    if st.session_state.pdf_data:
        st.download_button(
            label="📥 Download Official Exam PDF",
            data=st.session_state.pdf_data,
            file_name="CENTS_Full_Exam.pdf",
            mime="application/pdf"
        )
