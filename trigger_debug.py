# Trigger debug output
import requests
import time

print("Triggering home page...")
response = requests.get('http://127.0.0.1:5000/')
print(f"Status: {response.status_code}")
time.sleep(1)
print("Done")
