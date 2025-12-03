#!/usr/bin/env python3
import requests
import json
import sys
import os
from datetime import datetime

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
            lines = []
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            for row in data:
                values = [str(row.get(h, ""))[:50] for h in headers]
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

def main():
    print("=" * 60)
    print("BTC Map RPC Reports")
    print("=" * 60)
    print()
    
    print("Enter date range for trending reports (format: YYYY-MM-DD)")
    trending_start = get_date_input("Trending Start Date", "2025-11-01")
    trending_end = get_date_input("Trending End Date", "2025-11-30")
    
    print()
    print("Enter date range for the detailed report (times are inclusive)")
    print("Format: YYYY-MM-DD (time will be set to 00:00:00Z for start and 23:59:59Z for end)")
    report_start = get_date_input("Report Start Date", "2025-09-01")
    report_end = get_date_input("Report End Date", "2025-09-30")
    
    report_start_iso = f"{report_start}T00:00:00Z"
    report_end_iso = f"{report_end}T23:59:59Z"
    
    print()
    print("=" * 60)
    print()
    
    print("## Trending Countries")
    print(f"*Period: {trending_start} to {trending_end}*")
    print()
    result = call_rpc("get_trending_countries", {
        "period_start": trending_start,
        "period_end": trending_end
    })
    if result:
        print(format_generic_table(result))
    else:
        print("Failed to fetch trending countries.\n")
    
    print()
    print("## Trending Communities")
    print(f"*Period: {trending_start} to {trending_end}*")
    print()
    result = call_rpc("get_trending_communities", {
        "period_start": trending_start,
        "period_end": trending_end
    })
    if result:
        print(format_generic_table(result))
    else:
        print("Failed to fetch trending communities.\n")
    
    print()
    print("## Detailed Report")
    print(f"*Period: {report_start_iso} to {report_end_iso}*")
    print()
    result = call_rpc("get_report", {
        "start": report_start_iso,
        "end": report_end_iso
    })
    if result:
        print(format_generic_table(result))
    else:
        print("Failed to fetch report.\n")

if __name__ == "__main__":
    main()
