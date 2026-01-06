import streamlit as st
from groq import Groq
from pypdf import PdfReader
import io

# --- 1. Elegant Styling (Custom CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+Pro:wght@300;400&display=swap');
    html, body, [class*="css"] {
        font-family: 'Source Sans Pro', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
    }
    .stButton>button {
        background-color: #f0f2f6;
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ CENT-S Engine")
st.markdown("##### Professional Entrance Exam Generation")

# --- 2. Hidden Logic (Secrets) ---
# Ensure you have set 'GROQ_API_KEY' in your Streamlit Cloud Secrets!
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key not found in Secrets. Please add it to your app settings.")
    st.stop()

# --- 3. Simple Interface ---
st.header("Upload Context")
uploaded_file = st.file_uploader("Upload your master CENT-S PDF for style analysis", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    raw_text = "".join([page.extract_text() for page in reader.pages])
    st.success("Exam patterns analyzed.")

    if st.button("Generate Full CENT-S Exam"):
        # The 'Full Exam' Prompt with specific A, B, C, D formatting
        prompt = f"""
        Act as a professional CENT-S examiner. Study the following exam content:
        {raw_text[:4000]}
        
        TASK: Generate a COMPLETE new exam based on this context.
        FORMATTING RULES:
        1. Every question must have exactly 4 options labeled: a), b), c), d).
        2. Ensure the difficulty matches the provided text exactly.
        3. Do not include answers in the main text; list them at the very end.
        4. Style: Academic and formal.
        """
        
        with st.spinner("Compiling full exam..."):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            exam_output = completion.choices[0].message.content
            st.markdown("---")
            st.markdown(exam_output)
            
            # --- 4. Download Feature ---
            # Using a BytesIO buffer to allow the user to download the text as a file
            buf = io.BytesIO()
            buf.write(exam_output.encode())
            st.download_button(
                label="📥 Download Final Exam (.txt)",
                data=buf.getvalue(),
                file_name="CENTS_Generated_Exam.txt",
                mime="text/plain"
            )
