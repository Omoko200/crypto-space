import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

PAYSTACK = str(os.getenv("PAYSTACK"))

url = "https://api.paystack.co/transaction/initialize"

headers = {
    "Authorization": f"Bearer {PAYSTACK}",
    "Content-Type": "application/json",
}


data = {
    "email": "omokolouis@gmail.com",
    "amount": 5000 * 100,  # Amount in kobo
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())