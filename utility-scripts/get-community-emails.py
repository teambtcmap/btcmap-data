#This script retrieves the current list of community emails

import requests
import json
import sys
import os
from area import area as area_calc

# Get the bearer token from the environment variable
#btcmap_api_token = os.getenv("BTCMAP_API_TOKEN")

#if not btcmap_api_token:
#    print("Please set the BTCMAP_API_TOKEN environment variable.")
#    sys.exit(1)

# Define the API URL to fetch all areas
url = "https://api.btcmap.org/areas"
headers = {
    #'Authorization': f'Bearer {btcmap_api_token}',
    'Content-Type': 'application/json'
}

# Send a GET request to fetch all areas
response = requests.get(url)

if response.status_code != 200:
    print(f"Error fetching areas: {response.text}")
    sys.exit(1)

# Parse the response JSON
areas = response.json()

# Define the area type to filter (replace with your values)
area_type_filter = "community"

# Now, iterate through the features and treat each one as an area
for id in areas:
    tags = id.get('tags', None)
    area_type = tags.get('type')
    
    if area_type == area_type_filter:
    
        area_alias = tags.get('url_alias')
        email = tags.get('contact:email')

        if email is not None and email != "":
    
            print(f"{email},")

       