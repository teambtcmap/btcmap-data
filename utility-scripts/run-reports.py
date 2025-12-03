#!/usr/bin/env python3
"""
Run BTC Map reporting scripts.
"""

import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run_rpc_reports():
    """Run the RPC reports script."""
    subprocess.run([sys.executable, "rpc-reports.py"])

def run_fetch_communities(start_id=None, end_id=None):
    """Run the fetch communities script."""
    if start_id is None or end_id is None:
        print("\n" + "=" * 60)
        print("Fetch Communities")
        print("=" * 60)
        print()
        start_id = input("Start ID [900]: ").strip() or "900"
        end_id = input("End ID [950]: ").strip() or "950"
        print()
    
    subprocess.run([sys.executable, "fetch-communities.py", start_id, end_id])

def main():
    print("=" * 60)
    print("BTC Map Utility Scripts")
    print("=" * 60)
    print()
    print("1. RPC Reports (trending countries, communities, detailed report)")
    print("2. Fetch Communities (by ID range)")
    print("3. Run Both")
    print()
    
    choice = input("Select option [1]: ").strip() or "1"
    
    if choice == "1":
        run_rpc_reports()
    elif choice == "2":
        run_fetch_communities()
    elif choice == "3":
        print()
        print("Fetch Communities ID Range:")
        start_id = input("Start ID [900]: ").strip() or "900"
        end_id = input("End ID [950]: ").strip() or "950"
        print()
        
        run_rpc_reports()
        
        print("\n" + "=" * 60)
        print("Fetch Communities")
        print("=" * 60)
        print()
        run_fetch_communities(start_id, end_id)
    else:
        print("Invalid option")
        sys.exit(1)

if __name__ == "__main__":
    main()
