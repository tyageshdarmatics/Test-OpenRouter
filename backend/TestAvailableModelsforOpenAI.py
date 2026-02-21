from openai import OpenAI
import os
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.models.list()

table_data = []

for model in response.data:
    table_data.append([
        model.id,
        model.owned_by
    ])

print(tabulate(table_data,
            headers=["Model ID", "Owned By"],
            tablefmt="grid"))