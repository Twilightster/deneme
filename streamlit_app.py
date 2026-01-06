import streamlit as st

# 1. App Header
st.title("🚀 CENT-S Engine")
st.markdown("### AI-Powered Question Generator for University Entrance")

# 2. Upload Area
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

uploaded_file = st.file_uploader("Upload your current CENT-S questions (PDF or TXT)", type=["pdf", "txt"])

# 3. Logic Area
if uploaded_file:
    st.success("File uploaded! Analyzing the 'vibe' of your questions...")
    
    topic = st.text_input("What topic should the new questions be about?")
    num_questions = st.slider("Number of questions to generate", 1, 10, 3)

    if st.button("Generate Questions"):
        if not api_key:
            st.error("Please enter your API key in the sidebar first!")
        else:
            # This is where your AI 'Vibe' logic will live
            st.info(f"Generating {num_questions} questions about {topic}...")
            st.write("---")
            st.write("**Sample Question 1:** [AI Output will appear here]")
