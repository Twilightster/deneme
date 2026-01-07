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
            prompt = f"""
            Act as a CISIA Exam Designer. Generate a full 55-question CENT-S Scientific Exam.
            
            DISTRIBUTION: 15 Math, 15 Reasoning, 10 Bio, 10 Chem, 5 Physics.
            
            STRICT RULES:
            1. Use LaTeX for math/science (e.g., $log_{{2}}200$ or $CaCO_{{3}}$).
            2. For reasoning tables, use simple Markdown.
            3. Exactly 4 options (a, b, c, d). RANDOMIZE correct answers.
            4. Include an Answer Key at the very end.
            Context: {context_text[:3000]}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.exam_text = response.choices[0].message.content
            
            # --- PDF Generation with Safety Logic ---
            pdf = FPDF()
            pdf.add_page()
            try:
                # Using the verified font in your repo
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
                pdf.set_font("DejaVu", size=10)
            except:
                pdf.set_font("Helvetica", size=10)
            
            lines = st.session_state.exam_text.split('\n')
            for line in lines:
                # Detect and draw tables with horizontal safety
                if "|" in line and "--" not in line:
                    cols = [c.strip() for c in line.split("|") if c.strip()]
                    if cols:
                        # Calculate width: page width minus margins, divided by columns
                        effective_page_width = pdf.w - 2 * pdf.l_margin
                        col_width = effective_page_width / len(cols)
                        
                        # Use cell with precise width to prevent 'horizontal space' crash
                        for col in cols:
                            pdf.cell(col_width, 10, col, border=1)
                        pdf.ln()
                else:
                    # Normal text rendering
                    pdf.multi_cell(0, 8, txt=line)
            
            st.session_state.pdf_data = bytes(pdf.output())

    # 4. Results & Download
    if st.session_state.exam_text and st.session_state.pdf_data:
        st.markdown("---")
        st.markdown(st.session_state.exam_text)

        st.download_button(
            label="📥 Download Pro 55-Question PDF",
            data=st.session_state.pdf_data,
            file_name="CENTS_Engine_Full_Exam.pdf",
            mime="application/pdf"
        )
