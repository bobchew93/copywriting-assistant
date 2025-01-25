import streamlit as st
import requests
import time

# Set up the Streamlit app
st.title("Bob's Copywriting Assistant")  # Updated title
st.write("Generate high-quality copy in seconds.")

# Input fields
topic = st.text_input("Enter a topic:")
tone = st.selectbox("Choose a tone:", ["Formal", "Casual", "Persuasive", "Funny", "Inspirational"])
format = st.selectbox("Choose a format:", ["Email", "Social media post", "Blog post"])

# Get API key from Streamlit secrets
api_key = st.secrets.get("deepseek_api_key")
if not api_key:
    st.error("API key not found. Please check your Streamlit secrets configuration.")
    st.stop()

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
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)  # Add timeout
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# Generate copy when the user clicks the button
if st.button("Generate Copy"):
    if not topic or not tone or not format:
        st.warning("Please fill out all fields.")
    else:
        # Define the prompt based on the selected format
        if format.lower() == "email":
            prompt = f"Write a {tone.lower()} personality-driven email to promote {topic}."
        elif format.lower() == "social media post":
            prompt = f"Write a {tone.lower()} social media post about {topic}."
        elif format.lower() == "blog post":
            prompt = f"Write a {tone.lower()} blog post about {topic}."

        # Generate the copy using the API
        with st.spinner("Generating copy..."):
            progress_bar = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.01)  # Simulate a delay
                progress_bar.progress(percent_complete + 1)
            copy = generate_copy(prompt)

        # Display the generated copy
        if copy.startswith("Error:"):
            st.error(copy)  # Show error message in red
        else:
            st.subheader("Generated Copy:")
            st.write(copy)

            # Save the generated copy to a file
            try:
                with open("generated_copy.txt", "a", encoding="utf-8") as file:
                    file.write(f"Prompt: {prompt}\n")
                    file.write(f"Generated Copy:\n{copy}\n")
                    file.write("=" * 50 + "\n\n")
                st.success("Copy saved successfully!")  # Show success message

                # Add a download button
                st.download_button(
                    label="Download Copy",
                    data=copy,
                    file_name="generated_copy.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"Failed to save copy: {e}")
