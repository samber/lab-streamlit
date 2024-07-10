import os
import json
import streamlit as st
import pandas as pd
from io import StringIO
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

api_key = os.environ["OPENAI_API_KEY"]
model = "gpt-3.5-turbo"

llm = ChatOpenAI(model=model, api_key=api_key, temperature=0)

# Open a connection to the database.
# It can be a local sqlite file or a remote database.
db = SQLDatabase.from_uri("sqlite:///power-generation.sqlite")

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


def from_template(template, data):
    prompt_response = ChatPromptTemplate.from_template(template)
    text_response = (prompt_response | llm)
    return text_response.invoke(data)


def exec_sql_query(prompt):
    agent_executor = create_sql_agent(
        llm, db=db, agent_type="openai-tools")  # for debugging: verbose=True
    return agent_executor.invoke(prompt)['output']


def get_response_mode(prompt):
    template = """
Based on the following question, understand if the user has requested a line chart, a histogram, or none. Respond with only one of these options: histogram, line_chart, none.
Question: {question}
Response:"""
    return from_template(template, {"question": prompt}).content


def get_response_histogram(prompt):
    template = """
Based on the following results, write them in CSV format to pass them to the pandas library in a Dataframe using ';' as the separator if there are multiple columns, otherwise go to the next line, so that I can draw a histogram to answer the following question. Return a dictionary with the following fields: csv, column_names. Include the column names in the csv.
Numbers must be not separated by commas or dots.
Question: {question}
Results: {results}
Answer:"""
    csv = from_template(
        template, {"question": prompt, "results": exec_sql_query(prompt)})
    df = pd.read_csv(StringIO(json.loads(csv.content)['csv']), sep=';')
    columns = json.loads(csv.content)['column_names']
    st.dataframe(df)
    st.bar_chart(df, x=columns[0], y=columns[1])


def get_response_linechart(prompt):
    template = """
Based on the following results, write them in CSV format to pass them to the pandas library in a Dataframe using ';' as the separator if there are multiple columns, otherwise go to the next line, so that I can draw a line plot to answer the following question. Return a dictionary with the following fields: csv, column_names. Include the column names in the csv.
Numbers must be not separated by commas or dots.
Question: {question}
Results: {results}
Answer:"""
    csv = from_template(
        template, {"question": prompt, "results": exec_sql_query(prompt)})
    df = pd.read_csv(StringIO(json.loads(csv.content)['csv']), sep=';')
    st.dataframe(df)
    st.line_chart(df)


def get_response_text(prompt):
    response = exec_sql_query(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )


# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare response format based on user input
    mode = get_response_mode(prompt)
    print("Selected mode:", mode)
    if mode == "histogram":
        get_response_histogram(prompt)
    elif mode == "line_chart":
        get_response_linechart(prompt)
    else:
        get_response_text(prompt)
