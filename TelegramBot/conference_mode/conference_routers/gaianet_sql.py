import asyncio
import openai
import os
import json
from data.async_database import AsyncDataBase
from TelegramBot.settings.config import GAIANET_URL
from langchain.utilities import SQLDatabase
from langchain.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain

role_chat = """
Your custom role for gaianet chat
"""

# Initialize OpenAI client with custom GAIANET_URL
client = openai.OpenAI(base_url=GAIANET_URL)

# Initialize database connection
db = SQLDatabase.from_uri("URL_DATABASE")
db_chain = SQLDatabaseChain.from_llm(client, db, verbose=True, top_k=10)


async def chat_with_sql(query: str):
    """
    Function that sends a user's query to Gaianet, receives an SQL query,
    and executes it in the database to retrieve event IDs.

    :param query: User's natural language query
    :return: List of event IDs retrieved from the database
    """
    # Send the query to OpenAI's chat completion model
    response = db_chain.create(
        model="Phi-3-mini-4k-instruct-Q5_K_M",
        timeout=300,
        messages=[
            {"role": "system", "content": role_chat},  # Define the assistant's role
            {"role": "user", "content": query}  # User's query
        ],
        temperature=0.7,
        max_tokens=600
    )

    # Parse the response from OpenAI
    response_json = json.loads(response.json())

    # Initialize the AsyncDatabase instance to execute the generated SQL query
    database = AsyncDataBase()

    # Clean up the SQL query from the response
    answer = response_json['choices'][0]['message']['content'].replace('sql', '').replace('```', '')

    # Execute the query in the database
    result = await database.execute_query_for_gpt(query=answer)

    # Extract event IDs from the query results
    result_id = [event['id_event'] for event in result]

    return result_id
