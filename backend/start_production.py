#!/usr/bin/env python3
"""
Production startup script for Render.com deployment.
Consolidates all services into a single process suitable for Render's web service.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

# Handle Google Cloud credentials from environment variable
if os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"):
    try:
        creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        creds_path = "/tmp/google-credentials.json"
        with open(creds_path, "w") as f:
            f.write(creds_json)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        print(f"✓ Google Cloud credentials written to {creds_path}")
    except Exception as e:
        print(f"⚠ Failed to write Google Cloud credentials: {e}")

# Set production environment
os.environ["USE_REAL_AGENTS"] = "true"
os.environ["PRODUCTION"] = "true"

# Get the port Render assigns (default 10000 for local testing)
PRODUCTION_PORT = int(os.environ.get("PORT", 10000))
PRODUCTION_HOST = "http://127.0.0.1"
BASE_URL = f"{PRODUCTION_HOST}:{PRODUCTION_PORT}"

# IMPORTANT: Services communicate internally in the same process
# Since apps are mounted at specific paths (e.g., /inventory, /sales),
# and each service already includes its prefix in routes,
# we just need the base URL without additional prefixes

os.environ["SESSION_SERVICE_URL"] = BASE_URL
os.environ["DATA_SERVICE_URL"] = BASE_URL  
os.environ["SALES_AGENT_SERVICE_URL"] = BASE_URL

# Worker agents - they'll add their own path prefixes
os.environ["INVENTORY_SERVICE_URL"] = BASE_URL
os.environ["INVENTORY_URL"] = f"{BASE_URL}/inventory"  # For agent_client.py
os.environ["LOYALTY_SERVICE_URL"] = BASE_URL
os.environ["LOYALTY_URL"] = f"{BASE_URL}/loyalty"
os.environ["PAYMENT_SERVICE_URL"] = BASE_URL
os.environ["PAYMENT_URL"] = f"{BASE_URL}/payment"
os.environ["FULFILLMENT_SERVICE_URL"] = BASE_URL
os.environ["FULFILLMENT_URL"] = f"{BASE_URL}/fulfillment"
os.environ["POST_PURCHASE_SERVICE_URL"] = BASE_URL
os.environ["POST_PURCHASE_URL"] = f"{BASE_URL}/post-purchase"
os.environ["STYLIST_SERVICE_URL"] = BASE_URL
os.environ["STYLIST_URL"] = f"{BASE_URL}/stylist"
os.environ["RECOMMENDATION_SERVICE_URL"] = BASE_URL
os.environ["RECOMMENDATION_URL"] = f"{BASE_URL}/recommendation"
os.environ["VIRTUAL_CIRCLES_SERVICE_URL"] = BASE_URL
os.environ["VIRTUAL_CIRCLES_URL"] = f"{BASE_URL}/virtual-circles"
os.environ["AMBIENT_COMMERCE_SERVICE_URL"] = BASE_URL
os.environ["AMBIENT_COMMERCE_URL"] = f"{BASE_URL}/ambient"
os.environ["TELEGRAM_SERVICE_URL"] = BASE_URL

print(f"🔧 Production mode enabled")
print(f"📍 All services running on port {PRODUCTION_PORT}")
print(f"🔗 Internal communication via {BASE_URL}")

# Import FastAPI apps from all services
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create main application
app = FastAPI(
    title="EY CodeCrafters Backend",
    version="1.0.0",
    description="Production backend API for EY CodeCrafters"
)
print("FastAPI app created")

# Configure CORS - Update with your actual Vercel domain
allowed_origins = [
    "*",  # Allow all for now - UPDATE THIS with your Vercel domain
    # "https://your-vercel-app.vercel.app",
    # "http://localhost:5173",  # Local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and mount sub-applications
try:
    from auth_api import app as auth_app
    app.mount("/auth", auth_app)
    print("✓ Mounted Authentication API")
except Exception as e:
    print(f"⚠ Could not mount Authentication API: {e}")

try:
    from session_manager import app as session_app
    app.mount("/session", session_app)
    print("✓ Mounted Session Manager")
except Exception as e:
    print(f"⚠ Could not mount Session Manager: {e}")

try:
    from data_api import app as data_app
    app.mount("/data", data_app)
    print("✓ Mounted Data API")
except Exception as e:
    print(f"⚠ Could not mount Data API: {e}")

try:
    from agents.sales_agent.app import app as sales_app
    app.mount("/sales", sales_app)
    print("✓ Mounted Sales Agent")
except Exception as e:
    print(f"⚠ Could not mount Sales Agent: {e}")

try:
    from agents.worker_agents.inventory.app import app as inventory_app
    app.mount("/inventory", inventory_app)
    print("✓ Mounted Inventory Service")
except Exception as e:
    print(f"⚠ Could not mount Inventory: {e}")

try:
    from agents.worker_agents.loyalty.app import app as loyalty_app
    app.mount("/loyalty", loyalty_app)
    print("✓ Mounted Loyalty Service")
except Exception as e:
    print(f"⚠ Could not mount Loyalty: {e}")

try:
    from agents.worker_agents.payment.app import app as payment_app
    app.mount("/payment", payment_app)
    print("✓ Mounted Payment Service")
except Exception as e:
    print(f"⚠ Could not mount Payment: {e}")

try:
    from agents.worker_agents.fulfillment.app import app as fulfillment_app
    app.mount("/fulfillment", fulfillment_app)
    print("✓ Mounted Fulfillment Service")
except Exception as e:
    print(f"⚠ Could not mount Fulfillment: {e}")

try:
    from agents.worker_agents.post_purchase.app import app as post_purchase_app
    app.mount("/post-purchase", post_purchase_app)
    print("✓ Mounted Post Purchase Service")
except Exception as e:
    print(f"⚠ Could not mount Post Purchase: {e}")

try:
    from agents.worker_agents.stylist.app import app as stylist_app
    app.mount("/stylist", stylist_app)
    print("✓ Mounted Stylist Service")
except Exception as e:
    print(f"⚠ Could not mount Stylist: {e}")

try:
    from agents.worker_agents.recommendation.app import app as recommendation_app
    app.mount("/recommendation", recommendation_app)
    print("✓ Mounted Recommendation Service")
except Exception as e:
    print(f"⚠ Could not mount Recommendation: {e}")

try:
    from agents.worker_agents.virtual_circles.app import app as virtual_circles_app
    app.mount("/virtual-circles", virtual_circles_app)
    print("✓ Mounted Virtual Circles Service")
except Exception as e:
    print(f"⚠ Could not mount Virtual Circles: {e}")

try:
    from agents.worker_agents.ambient_commerce.app import app as ambient_app
    app.mount("/ambient", ambient_app)
    print("✓ Mounted Ambient Commerce Service")
except Exception as e:
    print(f"⚠ Could not mount Ambient Commerce: {e}")

try:
    from agents.worker_agents.telegram.app import app as telegram_app
    app.mount("/telegram", telegram_app)
    print("✓ Mounted Telegram Service")
except Exception as e:
    print(f"⚠ Could not mount Telegram: {e}")

@app.on_event("startup")
async def startup_event():
    # Load customer mappings in a thread
    import threading
    def load_data():
        from session_manager import load_customer_mappings
        load_customer_mappings()
        
        # Start scheduler
        from agents.worker_agents.fulfillment.app import scheduler
        if not scheduler.running:
            scheduler.start()
            print("Scheduler started")
    
    thread = threading.Thread(target=load_data)
    thread.start()

@app.get("/")
async def root():
    return {
        "service": "EY CodeCrafters Backend",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth",
            "session": "/session",
            "data": "/data",
            "sales": "/sales",
            "inventory": "/inventory",
            "loyalty": "/loyalty",
            "payment": "/payment",
            "fulfillment": "/fulfillment",
            "post_purchase": "/post-purchase",
            "stylist": "/stylist",
            "recommendation": "/recommendation",
            "virtual_circles": "/virtual-circles",
            "ambient": "/ambient",
            "telegram": "/telegram"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting server on port {port}")
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        raise
