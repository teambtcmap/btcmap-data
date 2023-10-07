#Python Script for creating areas in BTC Map API

import requests
import json
import sys
import os

# Get the bearer token from the environment variable
btcmap_api_token = os.getenv("BTCMAP_API_TOKEN")

if not btcmap_api_token:
    print("Please set the BTCMAP_API_TOKEN environment variable.")
    sys.exit(1)

url = "https://api.btcmap.org/areas"

headers = {
    'Authorization':f'Bearer {btcmap_api_token}',
    'Content-Type':'application/json'
}

area_data = {
    "id": "uk",
    "tags": {
        "type": "country",
        "name": "United Kingdom",
        "continent": "europe"
        }
}

json_payload = json.dumps(area_data)
print(json_payload)
sys.exit()

# Send the query to the Overpass API to get a list of node IDs
response = requests.post(url,headers=headers, data=json_payload)

# Check if the request was successful
if response.status_code == 200:
    print("Created")

else:
    print(f"Error: {response.text}")