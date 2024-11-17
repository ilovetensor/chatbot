from openai import OpenAI
import streamlit as st
import os
import json
from dotenv import load_dotenv
import pandas as pd

load_dotenv()  

st.set_page_config(page_title="My Space", page_icon="random", initial_sidebar_state="collapsed")



# Sidebar with text input for file path and drop-down for available files
with st.sidebar:
    passwd = st.text_input('password')

    if st.button('Clear History'):
        st.session_state.messages = []

if os.environ.get('PASSWORD_KEY', '') != '':
    if passwd == os.environ.get('PASSWORD_KEY_h'):
        st.write(pd.read_csv('history.csv'))
    if passwd != os.environ.get('PASSWORD_KEY'):
        st.error("User not allowed")
        st.stop()
else:
    st.error("set pwd key")
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

client = OpenAI()

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

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
