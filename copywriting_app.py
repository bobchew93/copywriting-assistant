import streamlit as st
import requests
import time

# Set up the Streamlit app
st.title("Bob's Copywriting Assistant")
st.write("Generate authentic, personality-driven copy that matches your style.")

# Context collection section
st.subheader("Tell me about yourself...")
personal_context = st.text_area(
    "Share relevant context about yourself and your brand voice (writing style, common phrases, tone, etc):",
    help="The more context you provide, the better I can match your voice"
)

# Additional context for specific content
content_context = st.text_area(
    "Any specific context for this piece? (target audience, recent events, background info, goals, etc):",
    help="Additional context helps create more relevant and targeted content"
)

# Regular input fields
topic = st.text_input("Enter a topic (what do you wanna talk about?):")
format = st.selectbox("Choose a format:", [
    "Facebook Post",
    "Email"
])

# Add tone selection
tone = st.selectbox("Choose a tone:", [
    "Casual",
    "Persuasive",
    "Funny",
    "Inspirational"
])

# Get API key from Streamlit secrets
api_key = st.secrets.get("deepseek_api_key")
if not api_key:
    st.error("API key not found. Please check your Streamlit secrets configuration.")
    st.stop()

url = "https://api.deepseek.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def generate_copy(prompt, personal_style, specific_context):
    system_prompt = f"""
    Personal Style Context:
    {personal_style}

    Specific Content Context:
    {specific_context}

    Please write in the authentic voice described above while incorporating the specific context provided.
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 750
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# Generate copy when the user clicks the button
if st.button("Generate Copy"):
    if not topic:
        st.warning("Please enter a topic.")
    else:
        # Enhanced prompt templates based on format and tone
        if format == "Facebook Post":
            prompt = f"Write a {tone.lower()} Facebook post about {topic}. Make it conversational and authentic while incorporating any specific context provided."
        elif format == "Email":
            prompt = f"Write a {tone.lower()} email about {topic}. Keep it personal and valuable while incorporating any specific context provided."
            
        # Generate the copy using the API
        with st.spinner("Creating your personalized content..."):
            progress_bar = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.01)
                progress_bar.progress(percent_complete + 1)
            copy = generate_copy(prompt, personal_context, content_context)
            
        # Display the generated copy
        if copy.startswith("Error:"):
            st.error(copy)
        else:
            st.subheader("Generated Copy:")
            st.write(copy)
            
            # Save the generated copy to a file
            try:
                with open("generated_copy.txt", "a", encoding="utf-8") as file:
                    file.write(f"Prompt: {prompt}\n")
                    file.write(f"Personal Context: {personal_context}\n")
                    file.write(f"Content Context: {content_context}\n")
                    file.write(f"Generated Copy:\n{copy}\n")
                    file.write("=" * 50 + "\n\n")
                st.success("Copy saved successfully!")
                
                # Add a download button
                st.download_button(
                    label="Download Copy",
                    data=copy,
                    file_name="generated_copy.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"Failed to save copy: {e}")
