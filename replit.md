# BTC Map Utilities

## Overview
Collection of Python utility scripts for working with BTC Map API data.

## Recent Changes
- **2025-11-06**: Added `fetch-communities.py` script to fetch community data from BTC Map API and generate markdown files

## Scripts

### fetch-communities.py
Fetches community data from the BTC Map API for a given range of area IDs and generates a Markdown file with formatted links.

**Usage:**
```bash
cd utility-scripts
python3 fetch-communities.py <start_id> <end_id> [output_file]
```

**Example:**
```bash
python3 fetch-communities.py 900 950 communities.md
```

**Output format:**
- Generates a Markdown file with bulleted list
- Each entry: `- [Community Name](https://btcmap.org/community/url-alias)`
- Automatically filters out IDs that don't have valid community data

**Features:**
- Handles HTTP errors gracefully
- Respects API rate limits with small delays between requests
- Shows progress during fetching
- Provides summary of results

## Dependencies
See `requirements.txt` for Python package dependencies.
