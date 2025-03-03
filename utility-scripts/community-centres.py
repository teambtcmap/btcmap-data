import sqlite3
import json
from shapely.geometry import shape, box
from shapely.ops import unary_union
from shapely.geometry import mapping

# Connect to SQLite database
conn = sqlite3.connect('btcmap.db')
cur = conn.cursor()

# Select geojson areas of type community
cur.execute("SELECT id, geojson FROM area WHERE type = 'community'")
areas = cur.fetchall()

for area_id, geojson_str in areas:
    features = json.loads(geojson_str)
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

    # Prepare new tags as JSON
    new_tags = json.dumps({
        'centroid': {'lat': lat, 'lon': lon},
        'bounding_box': mapping(bounding_box)
    })

    # Update the database with new tags
    cur.execute("UPDATE area SET tags = json_set(tags, '$.centroid', json(?), '$.bounding_box', json(?)) WHERE id = ?",
                (json.dumps({'lat': lat, 'lon': lon}), json.dumps(mapping(bounding_box)), area_id))

# Commit changes and close the connection
conn.commit()
conn.close()