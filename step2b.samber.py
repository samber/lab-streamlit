import os
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI

api_key = os.environ["OPENAI_API_KEY"]
model = "gpt-3.5-turbo"

llm = ChatOpenAI(model=model, api_key=api_key, temperature=0)

# Open a connection to the database.
# It can be a local sqlite file or a remote database.
db = SQLDatabase.from_uri("sqlite:///power-generation.sqlite")

agent_executor = create_sql_agent(
    llm, db=db, agent_type="openai-tools")  # for debugging: verbose=True

st.title("Echo")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
            "content": "Hi. I'm Jarviss. What can I do for you today?"},
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def get_response(prompt):
    return agent_executor.invoke(prompt)['output']


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
