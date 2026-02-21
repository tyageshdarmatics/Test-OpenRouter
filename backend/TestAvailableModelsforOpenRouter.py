import requests
import os
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

url = "https://openrouter.ai/api/v1/models"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Error:", response.text)
    exit()

models = response.json().get("data", [])

# table_data = []

# for model in models:
#     table_data.append([
#         model.get("id"),
#         model.get("context_length"),
#         model.get("pricing", {}).get("prompt"),
#     ])

# print(tabulate(table_data,
#             headers=["Model ID", "Context Length", "Prompt Price"],
#             tablefmt="grid"))


# New Version with free models highlighted
table_data = []

for model in models:
    pricing = model.get("pricing", {})
    prompt_price = pricing.get("prompt")

    try:
        if float(prompt_price) == 0:
            table_data.append([
                model.get("id"),
                model.get("context_length"),
                prompt_price,
            ])
    except (TypeError, ValueError):
        continue

print(tabulate(table_data,
            headers=["Model ID", "Context Length", "Prompt Price"],
            tablefmt="grid"))