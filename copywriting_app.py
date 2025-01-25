import streamlit as st
import requests
import time
from io import StringIO
from docx import Document  # For Word file support
import PyPDF2  # For PDF file support

# Set up the Streamlit app
st.title("Bob's Copywriting Assistant")
st.write("Generate authentic, personality-driven copy that matches your style.")

# Ensure API key is set up
try:
    api_key = st.secrets["deepseek_api_key"]
except KeyError:
    api_key = None
    st.warning("API key not found. Please configure your Streamlit secrets to use the API.")

# Initialize session state for storing uploaded text
if 'example_texts' not in st.session_state:
    st.session_state.example_texts = []

# Function to read files
def read_file(file):
    """Extract text from uploaded files (txt, docx, pdf)."""
    if file.name.endswith(".txt"):
        # Read plain text files
        return StringIO(file.getvalue().decode("utf-8")).read()
    elif file.name.endswith(".docx"):
        # Read Word files
        doc = Document(file)
        full_text = [p.text for p in doc.paragraphs]
        return '\n'.join(full_text)
    elif file.name.endswith(".pdf"):
        # Read PDFs
        pdf_reader = PyPDF2.PdfReader(file)
        full_text = [page.extract_text() for page in pdf_reader.pages]
        return '\n'.join(full_text)
    else:
        return None

# Upload section for examples
st.subheader("Upload Examples (Optional)")

uploaded_files = st.file_uploader(
    "Upload emails/posts/your love letter below...",
    type=['txt', 'docx', 'pdf'],
    accept_multiple_files=True,
    help="Upload up to 15 files • TXT, DOCX, PDF • Under 5MB per file recommended"  # Updated help text
)
# Add contextual inputs
st.subheader("Tell me about yourself...")
personal_context = st.text_area(
    "Share relevant context about yourself and your brand voice (writing style, common phrases, tone, etc):"
)

content_context = st.text_area(
    "Any specific context for this piece? (target audience, recent events, background info, goals, etc):"
)

# Topic and customization
topic = st.text_input("Enter a topic (what do you wanna talk about?):")
format = st.selectbox("Choose a format:", [
    "Facebook Post",
    "Email",
    "LinkedIn Post",
    "Tweet"
])

tone = st.selectbox("Choose a tone:", [
    "Casual",
    "Persuasive",
    "Funny",
    "Inspirational"
])

# Function to generate copy
def generate_copy(prompt, personal_style, specific_context, examples=[]):
    """Generate copy based on user input and examples."""
    examples_prompt = "\nWriting examples for reference:\n" if examples else ""
    for i, example in enumerate(examples, 1):
        examples_prompt += f"Example {i}:\n{example[:300]}...\n"  # Limit example text length
    
    system_prompt = f"""
    Personal Style Context:
    {personal_style}
    Specific Content Context:
    {specific_context}
    {examples_prompt}
    Style Guidelines:
    - Write in a natural, conversational tone
    - Avoid emojis and special formatting
    - Authentic, human-like storytelling
    Please generate content in the described tone and style.
    """

    try:
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 750
        }
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

# Generate Copy Button
if st.button("Generate Copy"):
    if not api_key:
        st.warning("Cannot generate copy: API key is missing.")
    elif not topic.strip():
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Creating your personalized content..."):
            prompt = f"Write a {tone.lower()} {format.lower()} about {topic}."
            result = generate_copy(prompt, personal_context, content_context, st.session_state.example_texts)
        
        # Display generated copy
        if result.startswith("Error:"):
            st.error(result)
        else:
            st.subheader("Generated Copy:")
            st.write(result)

# Footer with humor
st.markdown("---")
st.markdown("""
Have fun writing nonsense! No AI was harmed in the making of this app.

Built by me (Bob Chew, who takes no responsibility for your weird posts)
""")

