import streamlit as st
import requests
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import content_types

load_dotenv('.env')

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

st.set_page_config(layout="wide")

st.title("Startup Advisor Bot")

# Sidebar for chat history
st.sidebar.title("Chat History")

# Main chat area
chat_container = st.container()

# Input area
user_input = st.text_input("Type your message here:")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'current_chat' not in st.session_state:
    st.session_state.current_chat = []

# Choose a model
model = genai.GenerativeModel('gemini-1.5-flash')

# Instructions for the LLM
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
"""

# Function to start a new chat
def start_new_chat():
    st.session_state.current_chat = []
    chat = model.start_chat(history=[])
    return chat

# Function to display chat messages
def display_chat():
    for message in st.session_state.current_chat:
        with chat_container.chat_message(message["role"]):
            st.write(message["content"])

# Function to process user input
def process_user_input(user_input, chat):
    # Add user message to chat history
    st.session_state.current_chat.append({"role": "user", "content": user_input})
    
    # Get AI response
    response = chat.send_message(user_input)
    
    # Add AI response to chat history
    st.session_state.current_chat.append({"role": "assistant", "content": response.text})
    
    # Display updated chat
    display_chat()

# Main chat logic
if user_input:
    if not st.session_state.current_chat:
        chat = start_new_chat()
    else:
        # Convert chat history to Content objects
        history_contents = [content_types.Content(text=message["content"], role=message["role"]) for message in st.session_state.current_chat]
        chat = model.start_chat(history=history_contents)
    
    process_user_input(user_input, chat)

# Sidebar chat history
for i, chat in enumerate(st.session_state.chat_history):
    if st.sidebar.button(f"Chat {i+1}"):
        st.session_state.current_chat = chat

# Button to start a new chat
if st.sidebar.button("New Chat"):
    st.session_state.current_chat = []
    st.session_state.chat_history.append([])
