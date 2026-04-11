import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000/api"

def terminal_test():
    print("\n" + "="*50)
    print("🚀 ENERGY INTEL BACKEND - INTERACTIVE TERMINAL TEST")
    print("="*50)
    
    # 1. Fetch available branches
    print("\n[ACTION] Fetching branches...")
    try:
        resp = requests.get(f"{BASE_URL}/branches")
        branches = resp.json()
        print(f"[SUCCESS] Branches Found: {branches}")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return

    # 2. Manual Input Selection
    print("\n" + "-"*30)
    print("MAPPING 3-SITE DATA")
    print("-"*30)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"Using Date: {date_str}")
    
    for i in [1, 2, 3]:
        print(f"\n>> Input for Site {i}:")
        units = input(f"   Units (kWh) for Site {i}: ")
        cost = input(f"   Cost ($) for Site {i}: ")
        
        if units and cost:
            payload = {
                "branch_id": i,
                "units": float(units),
                "cost": float(cost),
                "date": date_str
            }
            res = requests.post(f"{BASE_URL}/manual-entry", json=payload)
            if res.status_code == 201:
                print(f"   [OK] Site {i} entry saved.")
            else:
                print(f"   [FAIL] Site {i} error: {res.text}")

    # 3. Verify Variation (Dashboard Comparison)
    print("\n" + "-"*30)
    print("COMPARING SITES")
    print("-"*30)
    for i in [1, 2, 3]:
        data = requests.get(f"{BASE_URL}/dashboard/{i}").json()
        total = data.get('analytics', {}).get('total_units', 0)
        print(f"Site {i} Total Consumption: {total} kWh")

    print("\nTest Complete. Refresh your webapp (http://localhost:5173) to see the variation!")

if __name__ == "__main__":
    terminal_test()
