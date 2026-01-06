import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader

st.title("🚀 CENT-S Engine")
st.markdown("### AI-Powered Question Generator")

# Secure way to handle API Key
api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

st.header("1. Upload Example Questions")
uploaded_file = st.file_uploader("Upload your CENT-S PDFs", type="pdf")

if uploaded_file and api_key:
    # Extract text from the PDF
    reader = PdfReader(uploaded_file)
    example_text = ""
    for page in reader.pages:
        example_text += page.extract_text()
    
    st.success("CENT-S examples analyzed!")

    st.header("2. Generate New Questions")
    topic = st.text_input("Target Topic (e.g., Mathematics, Logic)")
    num_q = st.slider("Number of questions", 1, 10, 3)

    if st.button("Generate Now"):
        client = OpenAI(api_key=api_key)
        
        # The 'Few-Shot' Vibe Prompt
        prompt = f"""
        You are the CENT-S Engine. 
        Study the formatting, difficulty, and style of these questions:
        {example_text[:2000]} 
        
        Now, generate {num_q} NEW questions about '{topic}' in that EXACT format.
        """
        
        with st.spinner("Creating questions..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            st.write(response.choices[0].message.content)
