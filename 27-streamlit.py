import streamlit as st

st.title("My RAG Agent")

# 1. Initialize the Memory Vault (Only happens once)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 2. Draw the existing conversation on the screen
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 3. Listen for new user input (The ':=' is called a Walrus Operator, it assigns and checks at the same time)
if user_input := st.chat_input("Type your message..."):
    # A. Instantly draw the user's message on the screen
    with st.chat_message("user"):
        st.write(user_input)
