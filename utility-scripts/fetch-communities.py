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

API_BASE = "https://api.btcmap.org/v3/areas"


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
    """Extract name, url_alias, and id from area data."""
    if not area_data or 'tags' not in area_data:
        return None
    
    tags = area_data['tags']
    name = tags.get('name')
    url_alias = tags.get('url_alias')
    area_id = area_data.get('id')
    
    if name and url_alias:
        return {
            'id': area_id,
            'name': name,
            'url_alias': url_alias
        }
    return None


def get_country_emoji(area_data):
    """Get country emoji from area data if available."""
    if not area_data or 'tags' not in area_data:
        return None
    
    tags = area_data['tags']
    # Check for country code in various tag formats
    country_code = tags.get('country_code') or tags.get('country')
    
    if country_code and len(country_code) == 2:
        # Convert 2-letter country code to emoji
        return ''.join(chr(ord(c) + 127397) for c in country_code.upper())
    
    return None


def is_integer(s):
    """Check if string is an integer."""
    try:
        int(s)
        return True
    except ValueError:
        return False


def generate_markdown(communities):
    """Generate and print markdown with community links."""
    print("\n## New Communities\n")
    
    if not communities:
        print("No new communities found.")
        return
    
    print("We welcomed the following new communities over the past month.\n")
    
    for community in communities:
        emoji = community.get('emoji', '')
        prefix = f"{emoji} " if emoji else ""
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
                # Get country emoji
                emoji = get_country_emoji(area_data)
                if emoji:
                    community_info['emoji'] = emoji
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
