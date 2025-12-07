"""
Seed script for payment gateway configurations
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
from redis_utils import redis_client

load_dotenv(backend_path / ".env")

def seed_payment_configs():
    """Seed payment gateway configurations"""
    r = redis_client
    
    print("💳 Seeding payment configurations...")
    print("-" * 50)
    
    # Payment gateway configs
    configs = {
        "payment:config:upi": {
            "enabled": True,
            "providers": ["paytm", "gpay", "phonepe"],
            "max_amount": 100000,
            "transaction_fee": 0
        },
        "payment:config:card": {
            "enabled": True,
            "providers": ["visa", "mastercard", "rupay"],
            "max_amount": 500000,
            "transaction_fee": 0.02  # 2%
        },
        "payment:config:wallet": {
            "enabled": True,
            "providers": ["paytm", "mobikwik", "freecharge"],
            "max_amount": 50000,
            "transaction_fee": 0.01  # 1%
        },
        "payment:config:netbanking": {
            "enabled": True,
            "providers": ["hdfc", "icici", "sbi", "axis"],
            "max_amount": 1000000,
            "transaction_fee": 0.015  # 1.5%
        }
    }
    
    for key, config in configs.items():
        r.set(key, str(config))
        print(f"✅ {key.split(':')[-1].upper()}: Configured")
    
    print("-" * 50)
    print(f"✅ Seeded {len(configs)} payment methods\n")
    
    # Verify
    print("🔍 Verification:")
    for key in list(configs.keys())[:3]:
        value = r.get(key)
        print(f"   {key}: {value if value else 'None'}")
    
    print("\n✅ Payment configurations seeded successfully!")

if __name__ == "__main__":
    seed_payment_configs()
