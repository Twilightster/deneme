import streamlit as st
from openai import OpenAI
from pypdf import PdfReader # Use 'pypdf' as it is the modern version

st.title("🚀 CENT-S Engine")
st.markdown("### AI-Powered Question Generator")

# 1. Sidebar for API Key
api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

st.header("1. Upload Example Questions")
uploaded_file = st.file_uploader("Upload your CENT-S PDFs", type="pdf")

# 2. Extract and Learn
if uploaded_file and api_key:
    reader = PdfReader(uploaded_file)
    # Extract text from all pages to 'teach' the AI the format
    raw_text = "".join([page.extract_text() for page in reader.pages])
    st.success(f"Analyzed {len(reader.pages)} pages of CENT-S context!")

    st.header("2. Generate New Questions")
    topic = st.text_input("Topic for new questions (e.g. Logic, Math)")
    num_q = st.slider("How many questions?", 1, 10, 3)

    if st.button("Generate Now"):
        client = OpenAI(api_key=api_key)
        # Few-Shot Prompt: Providing the example text tells AI the 'vibe'
        prompt = f"Study these CENT-S examples:\n{raw_text[:2000]}\n\nGenerate {num_q} NEW questions on '{topic}' in that EXACT format."
        
        with st.spinner("Engineering new questions..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            st.markdown("### Generated Questions")
            st.write(response.choices[0].message.content)
