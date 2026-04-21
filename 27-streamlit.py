import streamlit as st

st.title("My RAG Agent")

# 1. Initialize the Memory Vault (Only happens once)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 2. Draw the existing conversation on the screen
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

