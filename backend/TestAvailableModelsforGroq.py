# # Option 1 - Simple print
# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# api_key = os.getenv("GROQ_API_KEY")
# url = "https://api.groq.com/openai/v1/models"

# headers = {
#     "Authorization": f"Bearer {api_key}",
#     "Content-Type": "application/json"
# }

# response = requests.get(url, headers=headers)

# data = response.json()

# models = data.get("data", [])

# # Print table header
# print(f"{'Model ID':40} {'Owner':15} {'Context':10} {'Max Tokens':12} {'Active'}")
# print("-" * 90)

# # Print rows
# for model in models:
#     print(f"{model['id']:40} "
#         f"{model['owned_by']:15} "
#         f"{model['context_window']:10} "
#         f"{model['max_completion_tokens']:12} "
#         f"{model['active']}")


# # Option 2 
from tabulate import tabulate
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
url = "https://api.groq.com/openai/v1/models"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
models = response.json().get("data", [])

table_data = []

for model in models:
    table_data.append([
        model["id"],
        model["owned_by"],
        model["context_window"],
        model["max_completion_tokens"],
        model["active"]
    ])

headers = ["Model ID", "Owner", "Context Window", "Max Tokens", "Active"]

print(tabulate(table_data, headers=headers, tablefmt="grid"))