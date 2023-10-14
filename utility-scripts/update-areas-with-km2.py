#This script updates BTC Map areas of a given type with the KM^2 area of its GeoJSON.

import requests
import json
import sys
import os
from area import area as area_calc

# Get the bearer token from the environment variable
btcmap_api_token = os.getenv("BTCMAP_API_TOKEN")

if not btcmap_api_token:
    print("Please set the BTCMAP_API_TOKEN environment variable.")
    sys.exit(1)

# Define the API URL to fetch all areas
url = "https://api.btcmap.org/v2/areas"
headers = {
    'Authorization': f'Bearer {btcmap_api_token}',
    'Content-Type': 'application/json'
}

# Send a GET request to fetch all areas
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"Error fetching areas: {response.text}")
    sys.exit(1)

# Parse the response JSON
areas = response.json()

# Define the area type and area ID to filter (replace with your values)
target_area_type = "community"

# Now, iterate through the features and treat each one as an area
for id in areas:
    area_id = id.get('id')
    tags = id.get('tags', {})

    print(area_id)
    
    if tags.get('type') == target_area_type:
        geojson = tags.get('geo_json', {})
        features = geojson["features"]
        
        # Now you can work with the features, which is a list of GeoJSON features
        for feature in features:
        
            # Calculate the area of the geometry
            area_m2 = area_calc(feature.get("geometry"))
            area_km2 = round(area_m2 / 1_000_000)

            update_url = f"https://btcmap.org/areas/{area_id}/tags"

        # Define the payload to update the 'km2' tag
        update_payload = {
            'tags': [
                {
                    'area_km2': area_km2
                }
            ]
        }
    
        print(update_payload)

        # Send a PATCH request to update the 'km2' tag
        #response = requests.patch(update_url, headers=headers, json=update_payload)

        #if response.status_code == 200:
        #    print(f"Updated 'km2' for area ID {area_id} to {area_km2} km2")
        
        #else:
        #    print(f"Error updating 'km2' for area ID {area_id}: {response.text}")
