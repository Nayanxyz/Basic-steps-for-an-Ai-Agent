import streamlit as st

st.title("My Rag Agent")

message = st.chat_input("Type your message...")

if message:
    st.write(message)