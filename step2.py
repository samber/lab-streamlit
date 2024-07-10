from langchain_community.utilities import SQLDatabase

# Open a connection to the database.
# It can be a local sqlite file or a remote database.
db = SQLDatabase.from_uri("sqlite:///power-generation.sqlite")


def debug():
    print(db.dialect)
    print(db.get_usable_table_names())


def ask(query: str):
    return db.run(query)


# Here, we are executing an hard-coded query.
# Your job is to let the LLM generate the query.
print(ask("SELECT * FROM power_generation;"))
