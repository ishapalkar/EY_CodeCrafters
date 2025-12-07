"""
Comprehensive test script for Payment and Loyalty Agents
Tests all new features: authorization/capture, POS, timed promotions, rules engine
"""

import requests
import json
from datetime import datetime

# Base URLs
LOYALTY_URL = "http://localhost:8002"
PAYMENT_URL = "http://localhost:8003"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_loyalty_agent():
    """Test Loyalty Agent endpoints"""
    print_section("Testing Loyalty Agent")
    
    user_id = "user123"
    
    # 1. Check initial points
    print("\n1️⃣ Checking user points...")
    response = requests.get(f"{LOYALTY_URL}/loyalty/points/{user_id}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 2. Validate coupon
    print("\n2️⃣ Validating coupon 'ABFRL20'...")
    response = requests.get(f"{LOYALTY_URL}/loyalty/validate-coupon/ABFRL20")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 3. Apply loyalty (coupon + points)
    print("\n3️⃣ Applying loyalty benefits...")
    response = requests.post(f"{LOYALTY_URL}/loyalty/apply", json={
        "user_id": user_id,
        "cart_total": 1500.0,
        "applied_coupon": "ABFRL20",
        "loyalty_points_used": 50
    })
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    return result.get("final_total", 1500.0)

def test_payment_agent(amount):
    """Test Payment Agent endpoints"""
    print_section("Testing Payment Agent")
    
    user_id = "user123"
    
    # 1. Get payment methods
    print("\n1️⃣ Getting available payment methods...")
    response = requests.get(f"{PAYMENT_URL}/payment/methods")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 2. Process payment
    print(f"\n2️⃣ Processing payment of ₹{amount}...")
    response = requests.post(f"{PAYMENT_URL}/payment/process", json={
        "user_id": user_id,
        "amount": amount,
        "payment_method": "upi",
        "order_id": f"ORDER_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "metadata": {"source": "test_script"}
    })
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    transaction_id = result.get("transaction_id")
    
    # 3. Retrieve transaction
    if transaction_id:
        print(f"\n3️⃣ Retrieving transaction {transaction_id}...")
        response = requests.get(f"{PAYMENT_URL}/payment/transaction/{transaction_id}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return transaction_id

def test_full_flow():
    """Test complete purchase flow"""
    print_section("Complete Purchase Flow")
    
    print("\n📦 Scenario: User purchases items worth ₹1500")
    print("   - Applies 20% coupon (ABFRL20)")
    print("   - Redeems 50 loyalty points")
    print("   - Pays via UPI")
    
    # Step 1: Apply loyalty
    final_amount = test_loyalty_agent()
    
    # Step 2: Process payment
    transaction_id = test_payment_agent(final_amount)
    
    # Step 3: Award points (5% of purchase)
    if transaction_id:
        print("\n4️⃣ Awarding loyalty points for purchase...")
        points_earned = int(final_amount * 0.05)  # 5% cashback as points
        response = requests.post(f"{LOYALTY_URL}/loyalty/add-points", json={
            "user_id": "user123",
            "points": points_earned,
            "reason": f"Purchase - {transaction_id}"
        })
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print_section("Test Complete!")
    print(f"\n✅ Purchase flow completed successfully!")
    print(f"   Original: ₹1500.00")
    print(f"   Final: ₹{final_amount:.2f}")
    print(f"   Transaction: {transaction_id}")

def test_payment_authorization():
    """Test payment authorization and decline simulation"""
    print_section("TEST: Payment Authorization")
    
    payload = {
        "user_id": "user001",
        "amount": 1500.0,
        "payment_method": "card",
        "order_id": "ORD_TEST_001"
    }
    
    response = requests.post(f"{PAYMENT_URL}/payment/authorize", json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    return response.json().get("authorization_id")

def test_payment_capture(auth_id):
    """Test capturing authorized payment"""
    print_section("TEST: Payment Capture")
    
    if not auth_id:
        print("❌ Skipping - no authorization ID")
        return
    
    payload = {
        "authorization_id": auth_id,
        "amount": 1500.0
    }
    
    response = requests.post(f"{PAYMENT_URL}/payment/capture", json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_pos_payment():
    """Test POS terminal payment"""
    print_section("TEST: POS Payment")
    
    payload = {
        "store_id": "STORE_001",
        "terminal_id": "TERM_A12",
        "barcode": "8901234567890",
        "payment_method": "card",
        "amount": 2500.0
    }
    
    response = requests.post(f"{PAYMENT_URL}/payment/pos", json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_timed_promotions():
    """Test timed promotions engine"""
    print_section("TEST: Timed Promotions")
    
    # Check active promotions
    response = requests.get(f"{LOYALTY_URL}/loyalty/active-promotions")
    print("📋 All Promotions:")
    print(json.dumps(response.json(), indent=2))
    
    # Check applicable promotions
    payload = {
        "user_id": "user001",
        "cart_total": 1200.0,
        "category": "electronics"
    }
    
    response = requests.post(f"{LOYALTY_URL}/loyalty/check-promotions", json=payload)
    print("\n✅ Applicable Promotions:")
    print(json.dumps(response.json(), indent=2))

def test_loyalty_rules_engine():
    """Test loyalty points calculation with rules engine"""
    print_section("TEST: Loyalty Rules Engine")
    
    payload = {
        "user_id": "user001",
        "purchase_amount": 3500.0,
        "items_count": 7
    }
    
    response = requests.post(f"{LOYALTY_URL}/loyalty/calculate-points", json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    try:
        print("\n🚀 PAYMENT & LOYALTY AGENT - COMPREHENSIVE TESTS\n")
        
        # Original flow
        test_full_flow()
        
        # New features
        auth_id = test_payment_authorization()
        if auth_id:
            test_payment_capture(auth_id)
        
        test_pos_payment()
        test_timed_promotions()
        test_loyalty_rules_engine()
        
        print_section("✅ ALL TESTS COMPLETED")
        
    except requests.exceptions.ConnectionError as e:
        print("\n❌ Error: Could not connect to services")
        print("   Make sure both Loyalty and Payment agents are running:")
        print("   - Loyalty Agent: python backend/agents/worker_agents/loyalty/app.py")
        print("   - Payment Agent: python backend/agents/worker_agents/payment/app.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
