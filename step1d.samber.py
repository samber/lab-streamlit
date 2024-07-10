import os
import streamlit as st
from openai import OpenAI

api_key = os.environ["OPENAI_API_KEY"]
model = "gpt-3.5-turbo"

client = OpenAI(api_key=api_key)


st.title("Echo")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system",
            "content": "Be concise, and reply like a poet."},
        {"role": "assistant",
            "content": "Hi. I'm Charles Baudelaire. What can I do for you today?"},
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def get_response(prompt):
    messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]
    chat_response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return chat_response.choices[0].message.content


# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = get_response(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )