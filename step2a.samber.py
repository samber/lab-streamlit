import os
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


def debug():
    print(db.dialect)
    print(db.get_usable_table_names())


def ask(user_input: str):
    return agent_executor.invoke(user_input)['output']


print(ask("how many countries?"))
