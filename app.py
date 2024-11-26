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
    passwd = st.text_input('Password', type='password')

    if st.button('Clear History'):
        st.session_state.messages = []

if passwd == st.secrets['PASSWORD_KEY_h']:
    with open("history.csv", "r") as f:
        st.write(f.read())

if passwd != st.secrets['PASSWORD_KEY']:
    st.error("User not allowed")
    st.stop()

# Initialize chat history
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


uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "csv", "json"])
if uploaded_file:
    st.write(f"Uploaded file: {uploaded_file.name}")

    file_content = ""
    if uploaded_file.name.endswith(".txt"):
        file_content = uploaded_file.read().decode("utf-8")
        st.text_area("File Content", file_content, height=300)

    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        file_content = df.to_string()
        st.write(df)

    elif uploaded_file.name.endswith(".json"):
        file_content = json.dumps(json.load(uploaded_file), indent=2)
        st.json(file_content)

    elif uploaded_file.name.endswith(".pdf"):
        with st.spinner("Extracting text from PDF..."):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            file_content = "".join([page.extract_text() or "" for page in pdf_reader.pages])
            st.text_area("PDF Content", file_content, height=300)

    
    st.session_state.messages.append({
        "role": "system",
        "content": f"The user uploaded a file named '{uploaded_file.name}' with the following content:\n{file_content}"  # Truncate to 1000 characters
    })

    with st.chat_message("system"):
        st.markdown(f"File '{uploaded_file.name}' content has been added to the context.")


if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    
    with open('history.csv', 'a') as f:
        f.write(f'{prompt}\n')
    
    
    with st.chat_message("assistant"):
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=messages,
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
