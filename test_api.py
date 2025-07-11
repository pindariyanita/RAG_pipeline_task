import requests

# Replace query with your prompt
response = requests.post("http://127.0.0.1:8000/api/query/", json={"query": "What includes in Original Medicare?"})
print(response.json())
