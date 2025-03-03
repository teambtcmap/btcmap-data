
import sqlite3
import json
from shapely.geometry import shape, box
from shapely.ops import unary_union
from shapely.geometry import mapping

# Connect to SQLite database
conn = sqlite3.connect('btcmap.db')
cur = conn.cursor()

# Select areas of type community
cur.execute("SELECT id, tags FROM areas WHERE json_extract(tags, '$.type') = 'community'")
areas = cur.fetchall()

for area_id, tags_str in areas:
    tags = json.loads(tags_str)
    
    # Check if geo_json exists in tags
    if 'geo_json' not in tags:
        print(f"Area ID {area_id} does not have geo_json data, skipping...")
        continue
        
    geojson_data = tags['geo_json']
    
    # If the geo_json is a GeoJSON FeatureCollection
    if isinstance(geojson_data, dict) and 'type' in geojson_data and geojson_data['type'] == 'FeatureCollection':
        features = geojson_data
    else:
        # Create a default FeatureCollection with the geo_json as a feature
        features = {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'geometry': geojson_data}]}
    
    geometries = []

    for feature in features['features']:
        geometries.append(shape(feature['geometry']))

    # Create unary union of all geometries (poly & multi-poly)
    unified = unary_union(geometries)

    # Calculate the centroid
    centroid = unified.centroid
    lat, lon = centroid.y, centroid.x

    # Calculate the bounding box
    minx, miny, maxx, maxy = unified.bounds
    bounding_box = box(minx, miny, maxx, maxy)

    # Update the database with new tags
    cur.execute("UPDATE areas SET tags = json_set(tags, '$.centroid', json(?), '$.bounding_box', json(?)) WHERE id = ?",
                (json.dumps({'lat': lat, 'lon': lon}), json.dumps(mapping(bounding_box)), area_id))

# Commit changes and close the connection
conn.commit()
conn.close()
print("Community centers updated successfully!")
