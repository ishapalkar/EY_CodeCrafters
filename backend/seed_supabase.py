#!/usr/bin/env python3
"""
Seed Supabase with CSV data from backend/data folder.
Clears existing tables and loads exact data from CSVs.

Run: python seed_supabase.py
"""

import os
import csv
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
import requests

# Load environment
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().strip('"')
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip().strip('"')
DATA_DIR = Path(__file__).parent / "data"

# ==========================================
# CONFIGURATION
# ==========================================

BATCH_SIZE = 100  # Insert rows in batches

# Tables to seed (in order of dependencies)
# NOTE: idempotency MUST come before payments due to foreign key
TABLES_CONFIG = [
    # {
    #     "name": "stores",
    #     "csv_file": "stores.csv",
    #     "pk": "store_id"
    # },
    # {
    #     "name": "products",
    #     "csv_file": "products.csv",
    #     "pk": "sku"
    # },
    # {
    #     "name": "customers",
    #     "csv_file": "customers.csv",
    #     "pk": "customer_id"
    # },
    # {
    #     "name": "inventory",
    #     "csv_file": "inventory.csv",
    #     "pk": None  # No single PK, composite of sku + store_id
    # },
    # {
    #     "name": "orders",
    #     "csv_file": "orders.csv",
    #     "pk": "order_id"
    # },
    {
        "name": "idempotency",
        "csv_file": "idempotency.csv",
        "pk": "idempotency_key"
    },
    {
        "name": "payments",
        "csv_file": "payments.csv",
        "pk": "payment_id"
    },
]

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_headers() -> Dict[str, str]:
    """Get Supabase API headers."""
    return {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
    }

def validate_config():
    """Validate Supabase configuration."""
    if not SUPABASE_URL:
        print("❌ SUPABASE_URL not set in .env")
        return False
    if not SUPABASE_ANON_KEY:
        print("❌ SUPABASE_ANON_KEY not set in .env")
        return False
    print(f"✅ Supabase URL: {SUPABASE_URL}")
    return True

def read_csv_file(csv_file: str) -> List[Dict[str, Any]]:
    """
    Read CSV file and return list of rows as dictionaries.
    Converts data types appropriately.
    """
    csv_path = DATA_DIR / csv_file
    
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return []
    
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row or not any(row.values()):
                continue  # Skip empty rows
            
            # Clean up row data - convert types
            cleaned_row = {}
            for key, value in row.items():
                # Skip None/empty keys
                if not key:
                    continue
                
                # Handle empty/null values
                if value == '' or value is None:
                    cleaned_row[key] = None
                # Convert numeric fields
                elif key in ['loyalty_points', 'items_purchased', 'review count', 'qty', 'quantity', 'amount_rupees', 'customer_id', 'qty']:
                    try:
                        cleaned_row[key] = int(value)
                    except (ValueError, TypeError):
                        cleaned_row[key] = value
                elif key in ['price', 'ratings', 'msrp', 'total_spend', 'average_rating', 'discount_applied', 'gst', 'amount_rupees', 'rating']:
                    try:
                        cleaned_row[key] = float(value)
                    except (ValueError, TypeError):
                        cleaned_row[key] = value
                else:
                    cleaned_row[key] = value
            
            rows.append(cleaned_row)
    
    return rows

def clear_table(table_name: str) -> bool:
    """
    Delete all rows from a Supabase table.
    """
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    headers = get_headers()
    
    try:
        response = requests.delete(url, headers=headers, timeout=30)
        
        if response.status_code in [200, 204, 207]:
            print(f"   ✓ Table cleared")
            return True
        else:
            print(f"   ⚠️  Clear response: {response.status_code}")
            # Some responses might not return 204 but still work
            return True
            
    except Exception as e:
        print(f"   ❌ Error clearing table: {e}")
        return False

def insert_batch(table_name: str, batch: List[Dict[str, Any]]) -> bool:
    """
    Insert a batch of rows into a Supabase table.
    """
    if not batch:
        return True
    
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    headers = get_headers()
    
    try:
        response = requests.post(url, json=batch, headers=headers, timeout=30)
        
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"      ❌ Batch error {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"      ❌ Exception: {e}")
        return False

def seed_table(table_config: Dict[str, Any]) -> int:
    """
    Seed a single table with CSV data.
    Returns number of rows inserted.
    """
    table_name = table_config["name"]
    csv_file = table_config["csv_file"]
    
    print(f"\n📦 Seeding {table_name}...")
    
    # Read CSV
    rows = read_csv_file(csv_file)
    if not rows:
        print(f"   ❌ No data in {csv_file}")
        return 0
    
    print(f"   ✓ Read {len(rows)} rows from {csv_file}")
    
    # Clear existing data
    if not clear_table(table_name):
        return 0
    
    # Insert in batches
    inserted = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]
        
        if insert_batch(table_name, batch):
            inserted += len(batch)
            batch_num = i // BATCH_SIZE + 1
            print(f"   ✓ Batch {batch_num}: {len(batch)} rows → {inserted}/{len(rows)}")
        else:
            batch_num = i // BATCH_SIZE + 1
            print(f"   ❌ Batch {batch_num} failed - stopping")
            break
    
    if inserted == len(rows):
        print(f"✅ {table_name}: {inserted} rows inserted")
    else:
        print(f"⚠️  {table_name}: {inserted}/{len(rows)} rows inserted")
    
    return inserted

def main():
    """Main seeding function."""
    print("\n" + "=" * 70)
    print("🌱 SUPABASE SEEDING SCRIPT")
    print("=" * 70)
    print(f"Data directory: {DATA_DIR}\n")
    
    # Validate config
    if not validate_config():
        sys.exit(1)
    
    print()
    
    # Seed all tables
    total_inserted = 0
    for table_config in TABLES_CONFIG:
        try:
            inserted = seed_table(table_config)
            total_inserted += inserted
        except Exception as e:
            print(f"❌ Error seeding {table_config['name']}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(f"✅ SEEDING COMPLETE: {total_inserted} total rows inserted")
    print("=" * 70)
    print()
    print("📊 Next steps:")
    print("   1. Verify data in Supabase dashboard")
    print("   2. Enable FEATURE_SUPABASE_READ=true in .env")
    print("   3. Restart backend services")
    print()

if __name__ == "__main__":
    main()
