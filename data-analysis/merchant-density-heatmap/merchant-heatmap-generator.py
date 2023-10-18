import requests
import geopandas as gpd
import os
import numpy as np
import h3
import json  # Import the json module

# Set the working directory to the script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

# Step 1: Get Latest Merchants from btcmap.org/elements
url = "https://api.btcmap.org/elements"  # Updated URL
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
            lon = item['osm_json'].get('lon', None)
            lat = item['osm_json'].get('lat', None)

            # Only add entries with all necessary information
            if element_id is not None and lon is not None and lat is not None:
                element_info.append({'id': element_id, 'lon': lon, 'lat': lat})

        if element_info:
            # Create a GeoDataFrame from the location data
            gdf = gpd.GeoDataFrame(element_info, geometry=gpd.points_from_xy([float(e['lon']) for e in element_info], [float(e['lat']) for e in element_info]))

            # Define the hexagonal grid size in kilometers (adjust as needed)
            grid_size_km = 10.0

            # Create a hexagonal grid over the extent of the merchant data
            xmin, ymin, xmax, ymax = gdf.geometry.total_bounds
            grid = gpd.GeoDataFrame()
            grid['geometry'] = [h3.h3_to_geo(hex_id) for hex_id in h3.h3.polyfill(xmin, ymin, xmax, ymax, grid_size_km)]
            grid['hex_id'] = [h3.geo_to_h3(lon, lat, 8) for lon, lat in grid['geometry']]

            # Calculate hexagon-based density as merchants per square kilometer
            density = []
            for hex_id in grid['hex_id']:
                count = sum(1 for hex_id in gdf.geometry.apply(lambda point: h3.geo_to_h3(point.x, point.y, 8) == hex_id))
                density.append(count / (grid_size_km ** 2))  # Merchants per square kilometer
            grid['density'] = density

            # Save the density data as a shapefile in the current script directory
            shapefile_output = os.path.join(script_directory, 'merchant_density.shp')
            grid.to_file(shapefile_output)

            print(f"Merchant density exported as '{shapefile_output}'")
        else:
            print("No valid data found in the API response.")
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")