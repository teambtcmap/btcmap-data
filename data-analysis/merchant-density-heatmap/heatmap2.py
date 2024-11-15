import requests
import geopandas as gpd
import os
import numpy as np
import h3
import json
from shapely.geometry import box
import folium
from folium.plugins import HeatMap

# Set the working directory to the script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

# Step 1: Get Latest Merchants from btcmap.org/elements
url = "https://api.btcmap.org/v2/elements?updated_since=2022-10-11T00:00:00.000Z&limit=100000"  # Updated URL
response = requests.get(url)

# Check if the response status code indicates success
if response.status_code == 200:
    try:
        # Attempt to decode the JSON response
        data = response.json()

        # Step 2: Extract Element ID and Position (Lon, Lat)
        element_info = []
        for item in data:
            element_id = item.get('id', None)
            osm_json = item.get('osm_json', {})
            lon = osm_json.get('lon', None)
            lat = osm_json.get('lat', None)

            # Only add entries with all necessary information
            if element_id is not None and lon is not None and lat is not None:
                element_info.append({'id': element_id, 'lon': lon, 'lat': lat})

        if element_info:
            # Create a GeoDataFrame from the location data
            gdf = gpd.GeoDataFrame(element_info, geometry=gpd.points_from_xy(
                [float(e['lon']) for e in element_info],
                [float(e['lat']) for e in element_info]
            ))

            # Create a Folium map centered around the mean location
            mean_lat = gdf.geometry.y.mean()
            mean_lon = gdf.geometry.x.mean()
            heatmap = folium.Map(location=[mean_lat, mean_lon], zoom_start=12)

            # Prepare data for the heatmap
            heat_data = [[point.y, point.x] for point in gdf.geometry]

            # Create a heatmap layer
            HeatMap(heat_data).add_to(heatmap)

            # Save the heatmap to an HTML file
            heatmap_output = os.path.join(script_directory, 'merchant_heatmap.html')
            heatmap.save(heatmap_output)

            print(f"Heatmap exported as '{heatmap_output}'")
        else:
            print("No valid data found in the API response.")
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
