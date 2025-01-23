import requests
import geopandas as gpd
import os
import numpy as np
import h3
import geojson
import json
from shapely.geometry import box, shape
import folium
from folium.plugins import HeatMap

# Set the working directory to the script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

def fetch_merchant_data():
    url = "https://api.btcmap.org/v2/elements?updated_since=2022-10-11T00:00:00.000Z&limit=100000"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            data = response.json()
            element_info = []
            for item in data:
                element_id = item.get('id', None)
                osm_json = item.get('osm_json', {})
                lon = osm_json.get('lon', None)
                lat = osm_json.get('lat', None)
                if element_id is not None and lon is not None and lat is not None:
                    element_info.append({'id': element_id, 'lon': lon, 'lat': lat})
            return element_info
        except json.JSONDecodeError:
            print("Error decoding JSON response.")
            return []
    else:
        print(f"Failed to retrieve merchant data. Status code: {response.status_code}")
        return []

def fetch_area_data():
    url_areas = "https://api.btcmap.org/v3/areas?updated_since=2022-10-11T00:00:00.000Z&limit=1000"
    response_areas = requests.get(url_areas)
    
    if response_areas.status_code == 200:
        try:
            area_data = response_areas.json()
            return area_data
        except json.JSONDecodeError:
            print("Error decoding area JSON response.")
            return []
    else:
        print(f"Failed to retrieve area data. Status code: {response_areas.status_code}")
        return []

def create_heatmap_with_areas():
    merchant_info = fetch_merchant_data()
    area_data = fetch_area_data()

    if merchant_info:
        gdf = gpd.GeoDataFrame(
            merchant_info,
            geometry=gpd.points_from_xy(
                [float(e['lon']) for e in merchant_info],
                [float(e['lat']) for e in merchant_info])
        )

        mean_lat = gdf.geometry.y.mean()
        mean_lon = gdf.geometry.x.mean()
        heatmap = folium.Map(location=[mean_lat, mean_lon], zoom_start=12)

        heat_data = [[point.y, point.x] for point in gdf.geometry]
        HeatMap(heat_data).add_to(heatmap)

        for area in area_data:
            tags = area.get('tags', {})
            area_type = tags.get('type', None)
            if area_type == "community":
                geo_json = tags.get('geo_json', None)
                if geo_json:
                    parsed_geojson = geojson.loads(json.dumps(geo_json))
                    # Handle FeatureCollection or single Feature
                    if isinstance(parsed_geojson, geojson.FeatureCollection):
                        for feature in parsed_geojson.features:
                            geo_shape = shape(feature['geometry'])
                            area_gdf = gpd.GeoDataFrame(geometry=[geo_shape])
                            folium.GeoJson(
                                data=area_gdf.to_json(),
                                name=f"Community Area {area['id']}",
                                tooltip=area['id']
                            ).add_to(heatmap)
                    else:  # Assume a single Feature
                        geo_shape = shape(parsed_geojson['geometry'])
                        area_gdf = gpd.GeoDataFrame(geometry=[geo_shape])
                        folium.GeoJson(
                            data=area_gdf.to_json(),
                            name=f"Community Area {area['id']}",
                            tooltip=area['id']
                        ).add_to(heatmap)

        heatmap_output = os.path.join(script_directory, 'merchant_heatmap_with_community_areas.html')
        heatmap.save(heatmap_output)
        print(f"Heatmap with community areas exported as '{heatmap_output}'")
    else:
        print("No valid merchant data found.")

create_heatmap_with_areas()