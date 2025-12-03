#!/usr/bin/env python3
import requests
import json
import sys
import os
from datetime import datetime, date
from calendar import monthrange

RPC_URL = "https://api.btcmap.org/rpc"

btcmap_api_token = os.getenv("BTCMAP_API_TOKEN")

if not btcmap_api_token:
    print("Please set the BTCMAP_API_TOKEN environment variable.")
    sys.exit(1)

def call_rpc(method, params=None):
    """Call a JSON-RPC method on the BTC Map API."""
    if params is None:
        params = {}
    params["password"] = btcmap_api_token
    
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {btcmap_api_token}'
    }
    
    try:
        response = requests.post(RPC_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        
        if 'error' in result:
            print(f"RPC Error: {result['error']}")
            return None
        
        return result.get('result')
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def format_markdown_table(data, headers):
    """Format data as a markdown table."""
    if not data:
        return "No data returned.\n"
    
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    
    for row in data:
        values = [str(row.get(h, "")) if isinstance(row, dict) else str(v) for h, v in zip(headers, row if isinstance(row, (list, tuple)) else [row])]
        if isinstance(row, dict):
            values = [str(row.get(h, "")) for h in headers]
        lines.append("| " + " | ".join(values) + " |")
    
    return "\n".join(lines) + "\n"

def format_generic_table(data):
    """Format any data structure as a markdown table."""
    if not data:
        return "No data returned.\n"
    
    if isinstance(data, list) and len(data) > 0:
        if isinstance(data[0], dict):
            headers = list(data[0].keys())
            display_headers = [h for h in headers if h != 'url']
            lines = []
            lines.append("| " + " | ".join(display_headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(display_headers)) + " |")
            for row in data:
                values = []
                url = row.get('url', '')
                for h in display_headers:
                    val = str(row.get(h, ""))[:50]
                    if h == 'name' and url:
                        val = f"[{val}]({url})"
                    values.append(val)
                lines.append("| " + " | ".join(values) + " |")
            return "\n".join(lines) + "\n"
        else:
            return "\n".join([f"- {item}" for item in data]) + "\n"
    elif isinstance(data, dict):
        lines = ["| Key | Value |", "| --- | --- |"]
        for k, v in data.items():
            lines.append(f"| {k} | {str(v)[:50]} |")
        return "\n".join(lines) + "\n"
    else:
        return str(data) + "\n"

def get_date_input(prompt, default=None):
    """Get a date input from the user."""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def get_previous_month_defaults():
    """Calculate the first and last day of the previous month."""
    today = date.today()
    if today.month == 1:
        prev_year = today.year - 1
        prev_month = 12
    else:
        prev_year = today.year
        prev_month = today.month - 1
    
    first_day = date(prev_year, prev_month, 1)
    last_day = date(prev_year, prev_month, 30)
    
    return first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")

def main():
    print("=" * 60)
    print("BTC Map RPC Reports")
    print("=" * 60)
    print()
    
    default_start, default_end = get_previous_month_defaults()
    
    print("Enter date range (format: YYYY-MM-DD)")
    print("Times are inclusive for the report RPC")
    start_date = get_date_input("Start Date", default_start)
    end_date = get_date_input("End Date", default_end)
    
    start_iso = f"{start_date}T00:00:00Z"
    end_iso = f"{end_date}T23:59:59Z"
    
    print()
    print("=" * 60)
    print()
    
    print("## Trending Countries")
    print(f"*Period: {start_date} to {end_date}*")
    print()
    result = call_rpc("get_trending_countries", {
        "period_start": start_date,
        "period_end": end_date
    })
    if result:
        print(format_generic_table(result))
    else:
        print("Failed to fetch trending countries.\n")
    
    print()
    print("## Trending Communities")
    print(f"*Period: {start_date} to {end_date}*")
    print()
    result = call_rpc("get_trending_communities", {
        "period_start": start_date,
        "period_end": end_date
    })
    if result:
        print(format_generic_table(result))
    else:
        print("Failed to fetch trending communities.\n")
    
    print()
    print("## Detailed Report")
    print(f"*Period: {start_iso} to {end_iso}*")
    print()
    result = call_rpc("get_report", {
        "start": start_iso,
        "end": end_iso
    })
    if result:
        print(format_generic_table(result))
    else:
        print("Failed to fetch report.\n")

if __name__ == "__main__":
    main()
