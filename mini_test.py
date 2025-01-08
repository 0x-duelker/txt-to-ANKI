import requests

try:
    response = requests.get("https://httpbin.org/get")
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Error with requests module:", e)
