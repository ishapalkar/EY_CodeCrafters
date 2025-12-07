import os
from dotenv import load_dotenv
import redis

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise RuntimeError("Missing REDIS_URL in .env")

# Connect to Upstash Redis
client = redis.from_url(
    REDIS_URL,
    decode_responses=True
)

# Ping test
print("Pinging Redis...")
print("PING →", client.ping())

# Set a key
client.set("test:key", "hello-world")

# Get the key
value = client.get("test:key")
print("GET test:key →", value)

print("\n🎉 Redis test successful!")
