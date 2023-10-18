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
url = "https://api.btcmap.org/areas"
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
area_type_filter = "community"
area_alias_filter = "bansko-bitcoin"

# Now, iterate through the features and treat each one as an area
for id in areas:
    tags = id.get('tags', None)
    area_alias = tags.get('url_alias')
    area_type = tags.get('type')
    update_url = f"https://api.btcmap.org/areas/{area_alias}/tags"

    if area_type == area_type_filter:
        geojson = tags.get('geo_json', None)

        if geojson is not None:
                      
            # Calculate the area of the geometry
            area_m2 = area_calc(geojson)
            area_km2 = round(area_m2 / 1_000_000)

            if area_km2 != 0:
                
                # Define the payload to update the 'km2' tag
                area_km2_json = {
                                    "area_km2": area_km2
                                }

                payload = json.dumps(area_km2_json)
                
                # Send a PATCH request to update the 'km2' tag
                response = requests.patch(update_url, headers=headers, data=payload)

                if response.status_code == 200:
                    print(f"Updated 'km2' for area ID {area_alias} to {area_km2} km2")
                else:
                    print(f"Error updating {area_alias}: {response.text}")
            
            else:
                print(f"{area_alias} has an 0 KM2 value")
        
        else:

            print(f"{area_alias} does not have a geojson")