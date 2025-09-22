import streamlit as st
import requests

url = "http://localhost:8000/api/agent"

st.title("Agentic Workflow Chatbot")

if "history" not in st.session_state:
    st.session_state.history = []


def send_query():
    query = st.session_state.user_input

    if not query:
        return 

    st.session_state.history.append(("User", query))

    try:
        response = requests.post(url, json = {"query":query})

        answer = response.json().get("data","No response from backend")

    except Exception as e:
        answer = "Error: " + str(e)

    st.session_state.history.append(("Bot",answer))
    st.session_state.user_input = ""

st.text_input("Ask something: ", key = "user_input", on_change=send_query)

st.markdown("---")

for sender, msg in reversed(st.session_state.history):
    st.markdown(f"**{sender}:** {msg}")

if st.button("Clear chat"):
    st.session_state.history = []