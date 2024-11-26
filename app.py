from openai import OpenAI
import streamlit as st
import os
import json
from dotenv import load_dotenv
import pandas as pd
import PyPDF2

load_dotenv()

st.set_page_config(page_title="My Space", page_icon="random", initial_sidebar_state="collapsed")

# Sidebar with text input for file path and drop-down for available files
with st.sidebar:
    passwd = st.text_input('password', type='password')

    if st.button('Clear History'):
        st.session_state.messages = []

if passwd == st.secrets['PASSWORD_KEY_h']:
    with open("history.csv", "r") as f:
        st.write(f.read())

if passwd != st.secrets['PASSWORD_KEY']:
    st.error("User not allowed")
    st.stop()

# Load chat history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

cols = st.columns([6, 1])
with cols[0]:
    st.title("My Space")
with cols[1]:
    r = st.button("Rerun")
    if r:
        st.session_state.messages = []

client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# File uploading feature
uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "csv", "json"])
if uploaded_file:
    # Display file name
    st.write(f"Uploaded file: {uploaded_file.name}")

    # Process file (example: read and display content)
    if uploaded_file.name.endswith(".txt"):
        content = uploaded_file.read().decode("utf-8")
        st.text_area("File Content", content, height=300)

    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        st.write(df)

    elif uploaded_file.name.endswith(".json"):
        content = json.load(uploaded_file)
        st.json(content)

    elif uploaded_file.name.endswith(".pdf"):
        with st.spinner("Extracting text from PDF..."):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() or ""  # Handle pages with no text
            st.text_area("PDF Content", extracted_text, height=300)
            # Save extracted text for later use
            st.session_state["pdf_content"] = extracted_text


if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with open('history.csv', 'a') as f:
        f.write(f'{prompt}\n')
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
