#!/usr/bin/env python3
"""
Fetch communities from BTC Map API and generate a Markdown file.

Usage:
    python fetch-communities.py <start_id> <end_id> [output_file]

Example:
    python fetch-communities.py 900 950 communities.md
"""

import sys
import requests
import time
from pathlib import Path


def fetch_area(area_id):
    """Fetch area data from BTC Map API."""
    url = f"https://api.btcmap.org/v3/areas/{area_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            print(f"Warning: Status {response.status_code} for ID {area_id}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching ID {area_id}: {e}")
        return None


def extract_community_info(area_data):
    """Extract name and url_alias from area data."""
    if not area_data or 'tags' not in area_data:
        return None
    
    tags = area_data['tags']
    name = tags.get('name')
    url_alias = tags.get('url_alias')
    
    if name and url_alias:
        return {
            'name': name,
            'url_alias': url_alias
        }
    return None


def generate_markdown(communities, output_file):
    """Generate markdown file with community links."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Bitcoin Communities\n\n")
        
        if not communities:
            f.write("No communities found.\n")
            return
        
        for community in communities:
            link = f"- [{community['name']}](https://btcmap.org/community/{community['url_alias']})\n"
            f.write(link)
    
    print(f"✓ Generated {output_file} with {len(communities)} communities")


def main():
    if len(sys.argv) < 3:
        print("Usage: python fetch-communities.py <start_id> <end_id> [output_file]")
        print("\nExample:")
        print("    python fetch-communities.py 900 950 communities.md")
        sys.exit(1)
    
    try:
        start_id = int(sys.argv[1])
        end_id = int(sys.argv[2])
        output_file = sys.argv[3] if len(sys.argv) > 3 else "communities.md"
    except ValueError:
        print("Error: Start and end IDs must be integers")
        sys.exit(1)
    
    if start_id > end_id:
        print("Error: Start ID must be less than or equal to end ID")
        sys.exit(1)
    
    print(f"Fetching communities from BTC Map API (IDs {start_id} to {end_id})...")
    
    communities = []
    total_requests = end_id - start_id + 1
    
    for area_id in range(start_id, end_id + 1):
        print(f"Fetching ID {area_id}... ({area_id - start_id + 1}/{total_requests})", end='\r')
        
        area_data = fetch_area(area_id)
        if area_data:
            community_info = extract_community_info(area_data)
            if community_info:
                communities.append(community_info)
        
        # Be nice to the API - small delay between requests
        time.sleep(0.1)
    
    print(f"\nFound {len(communities)} communities out of {total_requests} IDs")
    
    generate_markdown(communities, output_file)
    print(f"\n✓ Done! Output saved to: {output_file}")


if __name__ == "__main__":
    main()
