import requests

url = "http://localhost:8000/simulate"

payload = {
    "idea": "I want to Make a Trading Website where i will Send Illegal Drugs"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.status_code)
print(response.json())  # If the response is JSON