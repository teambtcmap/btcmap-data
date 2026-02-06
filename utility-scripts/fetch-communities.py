#!/usr/bin/env python3
"""
Fetch new communities from BTC Map API starting from a given community.

Usage:
    python fetch-communities.py <start_community> [--max-empty N]

Examples:
    python fetch-communities.py rhode-island-bitcoiners
    python fetch-communities.py 1050
    python fetch-communities.py bitcoin-geneva --max-empty 3
"""

import sys
import requests
import time
import re
import reverse_geocoder as rg

API_BASE = "https://api.btcmap.org/v3/areas"


def calculate_centroid(geo_json):
    """Calculate centroid from GeoJSON Polygon coordinates."""
    if not geo_json or 'coordinates' not in geo_json:
        return None
    
    coordinates = geo_json['coordinates']
    if not coordinates or not isinstance(coordinates, list):
        return None
    
    # Handle Polygon (list of rings) or MultiPolygon (list of polygons)
    if isinstance(coordinates[0][0], list):
        # Polygon - use first ring
        ring = coordinates[0]
    else:
        # Single ring
        ring = coordinates
    
    if not ring:
        return None
    
    # Calculate centroid from all points
    lats = [point[1] for point in ring if len(point) >= 2]
    lons = [point[0] for point in ring if len(point) >= 2]
    
    if not lats or not lons:
        return None
    
    return (sum(lats) / len(lats), sum(lons) / len(lons))


def get_country_from_coordinates(lat, lon):
    """Get country code from coordinates using reverse geocoding."""
    try:
        result = rg.search((lat, lon))
        if result and len(result) > 0:
            return result[0].get('cc')
    except Exception as e:
        print(f"Warning: Reverse geocoding failed: {e}", file=sys.stderr)
    return None


def country_code_to_flag_emoji(country_code):
    """Convert 2-letter country code to flag emoji."""
    if not country_code or len(country_code) != 2:
        return None
    return ''.join(chr(ord(c) + 127397) for c in country_code.upper())


def fetch_area_by_id(area_id):
    """Fetch area data from BTC Map API by ID."""
    url = f"{API_BASE}/{area_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            print(f"Warning: Status {response.status_code} for ID {area_id}", file=sys.stderr)
            return None
    except requests.RequestException as e:
        print(f"Error fetching ID {area_id}: {e}", file=sys.stderr)
        return None


def fetch_area_by_alias(alias):
    """Fetch area data from BTC Map API by URL alias."""
    url = f"{API_BASE}/{alias}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            print(f"Warning: Status {response.status_code} for alias '{alias}'", file=sys.stderr)
            return None
    except requests.RequestException as e:
        print(f"Error fetching alias '{alias}': {e}", file=sys.stderr)
        return None


def extract_community_info(area_data):
    """Extract name, url_alias, id, and country flag from area data."""
    if not area_data or 'tags' not in area_data:
        return None
    
    tags = area_data['tags']
    name = tags.get('name')
    url_alias = tags.get('url_alias')
    area_id = area_data.get('id')
    
    if name and url_alias:
        community_info = {
            'id': area_id,
            'name': name,
            'url_alias': url_alias
        }
        
        # Get country from GeoJSON centroid
        geo_json = tags.get('geo_json')
        if geo_json:
            centroid = calculate_centroid(geo_json)
            if centroid:
                lat, lon = centroid
                country_code = get_country_from_coordinates(lat, lon)
                if country_code:
                    flag = country_code_to_flag_emoji(country_code)
                    if flag:
                        community_info['flag'] = flag
        
        return community_info
    return None





def is_integer(s):
    """Check if string is an integer."""
    try:
        int(s)
        return True
    except ValueError:
        return False


def generate_markdown(communities):
    """Generate and print markdown with community links and flags."""
    print("\n## New Communities\n")
    
    if not communities:
        print("No new communities found.")
        return
    
    print("We welcomed the following new communities over the past month.\n")
    
    for community in communities:
        flag = community.get('flag', '')
        prefix = f"{flag} " if flag else ""
        print(f"- {prefix}[{community['name']}](https://btcmap.org/community/{community['url_alias']})")
    
    print(f"\nWe now have 648+ Communities scattered across the planet. 🌎️")


def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch-communities.py <start_community> [--max-empty N]")
        print("\nExamples:")
        print("    python fetch-communities.py rhode-island-bitcoiners")
        print("    python fetch-communities.py 1050")
        print("    python fetch-communities.py bitcoin-geneva --max-empty 3")
        sys.exit(1)
    
    start_input = sys.argv[1]
    max_empty = 5  # Default: stop after 5 consecutive empty results
    
    # Parse optional --max-empty argument
    if '--max-empty' in sys.argv:
        try:
            max_empty_idx = sys.argv.index('--max-empty')
            max_empty = int(sys.argv[max_empty_idx + 1])
        except (ValueError, IndexError):
            print("Error: --max-empty requires an integer value", file=sys.stderr)
            sys.exit(1)
    
    # Determine if input is an ID or alias
    if is_integer(start_input):
        start_id = int(start_input)
        print(f"Starting from ID: {start_id}", file=sys.stderr)
    else:
        # It's an alias, fetch to get the ID
        print(f"Fetching community '{start_input}' to get ID...", file=sys.stderr)
        area_data = fetch_area_by_alias(start_input)
        if not area_data:
            print(f"Error: Could not find community '{start_input}'", file=sys.stderr)
            sys.exit(1)
        
        community_info = extract_community_info(area_data)
        if not community_info:
            print(f"Error: Could not extract info from community '{start_input}'", file=sys.stderr)
            sys.exit(1)
        
        start_id = community_info['id']
        print(f"Found '{community_info['name']}' with ID: {start_id}", file=sys.stderr)
    
    # Start from the next ID
    current_id = start_id + 1
    
    print(f"Fetching new communities starting from ID {current_id}...", file=sys.stderr)
    print(f"Will stop after {max_empty} consecutive empty results\n", file=sys.stderr)
    
    communities = []
    empty_count = 0
    total_checked = 0
    
    while empty_count < max_empty:
        print(f"Checking ID {current_id}... (found: {len(communities)}, empty streak: {empty_count})", end='\r', file=sys.stderr)
        
        area_data = fetch_area_by_id(current_id)
        total_checked += 1
        
        if area_data:
            community_info = extract_community_info(area_data)
            if community_info:
                communities.append(community_info)
                empty_count = 0  # Reset empty count on success
            else:
                empty_count += 1
        else:
            empty_count += 1
        
        current_id += 1
        time.sleep(0.1)  # Rate limiting
    
    print(f"\n\nFound {len(communities)} new communities (checked {total_checked} IDs)", file=sys.stderr)
    
    generate_markdown(communities)


if __name__ == "__main__":
    main()
