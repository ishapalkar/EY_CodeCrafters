# Seed loyalty points for test users

import os
import sys
from dotenv import load_dotenv
import redis

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise RuntimeError("Missing REDIS_URL in .env")

# Connect to Redis
client = redis.from_url(REDIS_URL, decode_responses=True)

# Test users with loyalty points
test_users = {
    "user001": 500,
    "user002": 1000,
    "user003": 250,
    "user004": 750,
    "user005": 1500,
    "user123": 300,
    "test_user": 2000,
    "anishka": 1200,
    "riddhi": 800,
}

print("🎯 Seeding loyalty points...")
print("-" * 50)

for user_id, points in test_users.items():
    key = f"user:{user_id}:points"
    client.set(key, points)
    print(f"✅ {user_id}: {points} points")

print("-" * 50)
print(f"✅ Seeded {len(test_users)} users with loyalty points")

# Verify
print("\n🔍 Verification:")
for user_id in list(test_users.keys())[:3]:
    key = f"user:{user_id}:points"
    points = client.get(key)
    print(f"   {user_id}: {points} points")

print("\n✅ Loyalty data seeded successfully!")
