import streamlit as st
import requests
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv('.env')

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

st.title("Startup Advisor Bot")

# Access your API key as an environment variable.
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
# Choose a model that's appropriate for your use case.
model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat(history=[])

# Instructions for the LLM (we'll use this later)
instructions = """
You are a specialized startup advisor in Canada, focused on connecting newcomer and minority founders with resources tailored to their unique needs (Model Role).
Your goal is to provide information on accelerators, incubators, funding opportunities, VCs, or other startup programs that are best suited to a user's circumstances and stage.
The user is a Startup Founder (User Role). You provide answers showing why that program is suited to the user & the link to the website of the specific programs recommended.
Here are some key considerations:
- **Accelerators:** Recommend accelerators that have a proven track record of supporting diverse founders.
- **Incubators:**  Highlight incubators that offer specific programs for newcomers or minority entrepreneurs.
- **Funding:**  Identify funding opportunities that are specifically designed for underrepresented founders.
- **VCs:**  Suggest VCs who have a history of investing in diverse startups.

Please follow these steps:
1. Greet the user and express enthusiasm for their entrepreneurial journey.
2. Ask the user to describe their startup idea or business model.
3. Ask the user to describe their stage & experience in building a startup.
4. Ask them to share their background (e.g., if they are a person of color, a recent immigrant, or a member of a specific community).
5. Summarize their information & request to confirm that you understood correctly. If necessary, ask clarifying questions.
6. Ignore any intermediate step where the user has provided relevant info in their prior input.
7. Verify links returned are live & contain relevant content before showing to user.
"""

# Initialize conversation history
conversation_history = []  # Start with an empty history

# Function to validate links
def is_link_valid(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Function to extract links from text
def extract_links_from_text(text):
    return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

# Sidebar
st.sidebar.title("Chat History")

# Display chat history in the sidebar
sidebar_chat_container = st.sidebar.empty()

# Chat interface
chat_container = st.container()

with chat_container:
    # Display the chat messages
    messages = st.empty()
    for message in conversation_history:
        if message.startswith("User Role:"):
            st.chat_message("user").write(message[10:])
        else:
            st.chat_message("assistant").write(message)

    # User input (make sure this is outside the 'with' block)
    user_input = st.text_input("Ask me anything about startup resources in Canada", key="user_input")

# Process user input (inside a loop)
while True:
    if user_input:
        try:
            conversation_history.append(f"User Role: {user_input}")
            # Send the instructions to the model ONLY on the first message
            if len(conversation_history) == 1:
                response = chat.send_message(instructions)
                # Don't add the instructions to the conversation history
                # conversation_history.append(response.text) 
            else:
                response = chat.send_message(conversation_history[-1])
            links = extract_links_from_text(response.text)
            valid_links = [link for link in links if is_link_valid(link)]
            for link, valid_link in zip(links, valid_links):
                response.text = re.sub(r'\b' + re.escape(link) + r'\b', valid_link, response.text)
            conversation_history.append(response.text)
            # Store the response in session state
            st.session_state.responses = st.session_state.get('responses', []) + [response.text]
            # Clear the user input field
            user_input = ""  # Clear the input field directly
            # Display the response
            st.chat_message("assistant").write(response.text)
            # Update the sidebar chat history
            sidebar_chat_container.write(f"**Assistant:** {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching links: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    # Update the user input field
    user_input = st.text_input("Ask me anything about startup resources in Canada", key="user_input")

# Clear chat history button
if st.sidebar.button("Clear Chat History"):
    conversation_history.clear()
    st.session_state.responses = []  # Clear stored responses
    sidebar_chat_container.empty()  # Clear the sidebar content
    # Clear the user input field using the key
    st.session_state["user_input"] = ""  # Clear the input field directly
    # Update the sidebar chat history
    sidebar_chat_container.write(f"**Assistant:** {response.text}")

# Display stored responses (if any)
if 'responses' in st.session_state:
    st.markdown("## Stored Responses:")
    for response in st.session_state.responses:
        st.write(response)
