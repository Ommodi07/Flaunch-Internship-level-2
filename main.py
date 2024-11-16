import streamlit as st
from langchain_groq import ChatGroq

groq_api = "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"

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    groq_api_key=groq_api
)

st.title("HealBot")
st.write("Enter your problem:")

user_input = st.text_input("")
if st.button("Submit") and user_input:
    response = llm.invoke(f"""
        Create a description like a doctor gives to the patient for the given problem in just 4-5 lines, including medicines if required: {user_input}
    if the problem is not related to healthcare then give a discription in 4 lines that i can't provide you furthure in this problem.
    """)
    st.success(f"HealBot: {response.content}")
