import sqlite3
import json
from shapely.geometry import shape, box
from shapely.ops import unary_union
from shapely.geometry import mapping

# Connect to SQLite database
conn = sqlite3.connect('btcmap.db')
cur = conn.cursor()

# Select areas of type community
cur.execute("SELECT id, tags FROM area WHERE json_extract(tags, '$.type') = 'community'")
areas = cur.fetchall()

for area_id, tags_str in areas:
    try:
        tags = json.loads(tags_str)

        # Check if geo_json exists in tags
        if 'geo_json' not in tags:
            print(f"Area ID {area_id} does not have geo_json data, skipping...")
            continue

        geojson_data = tags['geo_json']
        geometries = []

        # If the geo_json is a GeoJSON FeatureCollection
        if isinstance(geojson_data, dict) and 'type' in geojson_data:
            if geojson_data['type'] == 'FeatureCollection' and 'features' in geojson_data:
                # Handle FeatureCollection
                for feature in geojson_data['features']:
                    try:
                        geom = shape(feature['geometry'])
                        geometries.append(geom)
                    except (ValueError, IndexError, KeyError) as e:
                        print(f"Error processing feature in area {area_id}: {e}")
                        continue
            else:
                # Handle single geometry
                try:
                    geom = shape(geojson_data)
                    geometries.append(geom)
                except (ValueError, IndexError, KeyError) as e:
                    print(f"Error processing geometry in area {area_id}: {e}")
                    continue

        if not geometries:
            print(f"No valid geometries found for area {area_id}, skipping...")
            continue

        # Create unary union of all geometries (poly & multi-poly)
        unified = unary_union(geometries)

        # Calculate the centroid
        centroid = unified.centroid
        lat, lon = centroid.y, centroid.x

        # Calculate the bounding box coordinates
        minx, miny, maxx, maxy = unified.bounds
        
        # Create a bbox array in GeoJSON format [west, south, east, north]
        bbox_array = [minx, miny, maxx, maxy]
        
        # First update the centroid
        cur.execute("UPDATE area SET tags = json_set(tags, '$.centroid', json(?)) WHERE id = ?",
                   (json.dumps({'lat': lat, 'lon': lon}), area_id))
        
        # Then add the bbox to the geo_json structure according to GeoJSON spec
        cur.execute("""
            UPDATE area 
            SET tags = json_set(
                tags, 
                '$.geo_json.bbox', 
                json(?)
            ) 
            WHERE id = ?
        """, (json.dumps(bbox_array), area_id))

        print(f"Successfully processed area {area_id}")

    except Exception as e:
        print(f"Error processing area {area_id}: {e}")
        continue

# Commit changes and close the connection
conn.commit()
conn.close()
print("Community centers updated successfully!")