import streamlit as st
import requests

# Set up the Streamlit app
st.title("AI-Powered Copywriting Assistant")
st.write("Generate high-quality copy in seconds!")

# Input fields
topic = st.text_input("Enter a topic:")
tone = st.selectbox("Choose a tone:", ["professional", "casual", "persuasive"])
format = st.selectbox("Choose a format:", ["email", "social media post", "blog post"])

# Get API key from Streamlit secrets
api_key = st.secrets["deepseek_api_key"]
url = "https://api.deepseek.com/v1/chat/completions"

# Set up the headers with your API key
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def generate_copy(prompt):
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}\n{response.text}"

# Generate copy when the user clicks the button
if st.button("Generate Copy"):
    if not topic:
        st.warning("Please enter a topic.")
    else:
        if format.lower() == "email":
            prompt = f"Write a {tone} personality-driven email to promote {topic}."
        elif format.lower() == "social media post":
            prompt = f"Write a {tone} social media post about {topic}."
        elif format.lower() == "blog post":
            prompt = f"Write a {tone} blog post about {topic}."
            
        copy = generate_copy(prompt)
        st.subheader("Generated Copy:")
        st.write(copy)
        
        with open("generated_copy.txt", "a", encoding="utf-8") as file:
            file.write(f"Prompt: {prompt}\n")
            file.write(f"Generated Copy:\n{copy}\n")
            file.write("=" * 50 + "\n\n")
