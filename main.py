import streamlit as st
from langchain_groq import ChatGroq

groq_api = "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"
llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    groq_api_key=groq_api
)

st.title("HealBot 🩺🤖")
st.write("Enter your problem:")

if "chat" not in st.session_state:
    st.session_state.chat = []

user_input = st.text_input("")

if st.button("Submit") and user_input:
    response = llm.invoke(f"""
        Create a description like a doctor gives to the patient for the given problem in just 4-5 lines, including medicines if required: {user_input}
        If the problem is related to greeting than greet back as response
        If the problem is not related to healthcare, give a description in 4 lines that I can't assist further with this problem.
    """)
    
    st.session_state.chat.append({"user": user_input, "bot": response.content})

st.write("##### Chat Box ")
if st.session_state.chat:
    for entry in reversed(st.session_state.chat):
        st.markdown(f"You : {entry['user']}")
        st.markdown(f"HealBot : {entry['bot']}")
else:
    st.write("No Chats.")
