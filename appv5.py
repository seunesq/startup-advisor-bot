import streamlit as st
import requests
import os
import re  # Import for regular expressions
from dotenv import load_dotenv  # Import dotenv

import google.generativeai as genai

load_dotenv('.env') # Load environment variables from .env

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

st.title("Resources for Underrepresented Founders in Canada") 

# Access your API key as an environment variable.
genai.configure(api_key = os.environ['GOOGLE_API_KEY'])
# Choose a model that's appropriate for your use case.
model = genai.GenerativeModel('gemini-1.5-flash')
chat=model.start_chat(history=[])

# Instructions for the LLM
instructions = """
You are a startup advisor in Canada (Model Role). You are responsible for connecting newcomer founders and minority founders to resources to support their entrepreneurship journey. 
You provide information on accelerators, incubators, funding opportunities, VCs, or other startup programs that are best suited to a user's circumstances and stage.
The user is a Startup Founder (User Role). You provide answers showing why that program is suited to the user & the link to the website of the specific programs recommended
Please follow these steps:
1. Greet the user and praise them for embarking on the entrepreneurial journey:**.
2. Ask the user to provide information on what they are looking for or need help with:** 
3. Ask the user to describe their stage & experience in building a startup:**
4. Ask them to notify you if they are a person of colour or a recent immigrant so you can provide targeted resources**
5. Summarize their information & request to confirm that you understood correctly:** If necessary, ask clarifying questions
6. Ignore any intermediate step where the user has provided relevant info in their prior input
7. Verify links returned are live & contain relevant content before showing to user.
"""


response = chat.send_message(instructions)
st.write(response.text)

# User input field
user_question = st.text_area("Ask your question about startup resources:", key="initial_question")

def is_link_valid(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def extract_links_from_text(text):
    return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

# Initialize conversation history
conversation_history = [instructions]

if user_question:
  conversation_history.append(f"User Role: {user_question}")  # Prepend user role
  response = chat.send_message(conversation_history[-1])  # Send the message with role
  # Extract links from the response
  links = extract_links_from_text(response.text)  # Implement this function

  # Validate each link
  valid_links = [link for link in links if is_link_valid(link)]

  # Display the response with only valid links
  for link, valid_link in zip(links, valid_links):
      response.text = re.sub(r'\b' + re.escape(link) + r'\b', valid_link, response.text)
  st.write(response.text) 
  # Keep the conversation going
  i = 0
  while True:
    user_input = st.text_area("Continue the conversation:", key=f"conversation_input_{i}") # Use a unique key
    if user_input:
      conversation_history.append(f"User Role: {user_input}")  # Prepend user role
      response = chat.send_message(conversation_history[-1])  # Send the message with role
      # Extract links from the response
      links = extract_links_from_text(response.text)  # Implement this function

      # Validate each link
      valid_links = [link for link in links if is_link_valid(link)]

      # Display the response with only valid links
      for link, valid_link in zip(links, valid_links):
          response.text = re.sub(r'\b' + re.escape(link) + r'\b', valid_link, response.text)
      st.write(response.text) 
      i += 1 # Increment the counter for the next iteration
    else:
      break
