import csv
from datetime import datetime, timedelta

# INPUT FILES (PUT YOUR FILE NAMES HERE)
SKU_FILE = "merged_products.csv"
STORE_FILE = "stores.csv"
IDEMPOTENCY_FILE = "idempotency.csv"

# OUTPUT FILE
HOLDS_FILE = "holds.csv"

# Load SKU list
with open(SKU_FILE, "r") as f:
    reader = csv.DictReader(f)
    skus = [row["sku"] for row in reader]

# Load store list
with open(STORE_FILE, "r") as f:
    reader = csv.DictReader(f)
    stores = [row["store_id"] for row in reader]

# Load idempotency + created_at
with open(IDEMPOTENCY_FILE, "r") as f:
    reader = csv.DictReader(f)
    idempo_rows = list(reader)

# Create holds.csv
with open(HOLDS_FILE, "w", newline="") as f:
    writer = csv.writer(f)

    # HEADER ROW
    writer.writerow([
        "hold_id", "sku", "store_id", "qty",
        "session_id", "created_at", "expires_at",
        "paid", "idempotency_key"
    ])

    hold_counter = 1

    for i, idrow in enumerate(idempo_rows):
        hold_id = f"HOLD_{hold_counter:06d}"  # HOLD_000001 format

        sku = skus[i % len(skus)]           # sequential SKU
        store = stores[i % len(stores)]     # sequential store

        # created_at from idempotency
        created_at = idrow["created_at"]
        created_dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")

        # expiry = +15 minutes
        expires_dt = created_dt + timedelta(minutes=15)
        expires_at = expires_dt.strftime("%Y-%m-%d %H:%M:%S")

        # dummy session id
        session_id = f"SESSION_{i+1:05d}"

        writer.writerow([
            hold_id,
            sku,
            store,
            1,                                # qty = 1 (change if needed)
            session_id,
            created_at,
            expires_at,
            "false",                          # paid default false
            idrow["idempotency_key"]          # like idemp_PAY000997
        ])

        hold_counter += 1

print("🎉 holds.csv generated successfully!")
