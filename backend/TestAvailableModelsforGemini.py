import google.generativeai as genai
import os
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

models = genai.list_models()

table_data = []

for model in models:
    table_data.append([
        model.name,
        model.supported_generation_methods
    ])

print(tabulate(table_data,
            headers=["Model Name", "Supported Methods"],
            tablefmt="grid"))