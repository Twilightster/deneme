import streamlit as st
from groq import Groq
from pypdf import PdfReader

st.title("🚀 CENT-S Engine (Free Edition)")
st.markdown("### Powered by Groq & Llama 3")

# 1. Sidebar for FREE Groq Key
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

st.header("1. Upload Example Questions")
uploaded_file = st.file_uploader("Upload your CENT-S PDF", type="pdf")

if uploaded_file and api_key:
    # Read the PDF text
    reader = PdfReader(uploaded_file)
    raw_text = "".join([page.extract_text() for page in reader.pages])
    st.success("CENT-S vibe analyzed for free!")

    st.header("2. Generate New Questions")
    topic = st.text_input("Topic for new questions")
    num_q = st.slider("Quantity", 1, 10, 3)

    if st.button("Generate Now"):
        client = Groq(api_key=api_key)
        
        # Training the AI on your specific vibe
        prompt = f"""
        Analyze these CENT-S exam questions for style and format:
        {raw_text[:3000]}
        
        Now, generate {num_q} NEW questions on '{topic}' that match this format exactly.
        """
        
        with st.spinner("Groq is working at lightning speed..."):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.markdown("### Generated Questions")
            st.write(completion.choices[0].message.content)
