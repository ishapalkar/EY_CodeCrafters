"""
Test script for the Sales Conversation Layer.

This script tests the SalesConversationEngine across all conversation states
to verify that the LLM integration, prompts, rules, and fallback templates
are working correctly.

Run from the sales_agent directory:
    py test_conversation_layer.py
"""

import sys
import os

# Add the parent 'agents' directory to sys.path so we can import sales_agent as a package
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_dir = os.path.dirname(current_dir)
if agents_dir not in sys.path:
    sys.path.insert(0, agents_dir)

from sales_agent.engine import SalesConversationEngine


def test_discovery_state():
    """Test the DISCOVERY conversation state."""
    print("\n" + "="*80)
    print("TEST 1: DISCOVERY State")
    print("="*80)
    
    engine = SalesConversationEngine()
    context = {
        "customer_name": "Sarah",
        "products": ["Classic Leather Sneaker", "Running Shoes Pro"],
        "occasion": "casual everyday wear"
    }
    event = "Customer enters store and browses the shoe section"
    
    response = engine.generate_response("DISCOVERY", context, event)
    print(f"Response:\n{response}\n")


def test_comparison_state():
    """Test the COMPARISON conversation state."""
    print("\n" + "="*80)
    print("TEST 2: COMPARISON State")
    print("="*80)
    
    engine = SalesConversationEngine()
    context = {
        "customer_name": "Mike",
        "products": ["Running Shoes Pro ($120)", "Athletic Trainer ($95)"],
        "comparison_criteria": "durability and cushioning"
    }
    event = "Customer asks about differences between two running shoes"
    
    response = engine.generate_response("COMPARISON", context, event)
    print(f"Response:\n{response}\n")


def test_gifting_state():
    """Test the GIFTING conversation state."""
    print("\n" + "="*80)
    print("TEST 3: GIFTING State")
    print("="*80)
    
    engine = SalesConversationEngine()
    context = {
        "customer_name": "Jessica",
        "recipient": "her sister",
        "occasion": "birthday",
        "budget": "$80-100",
        "products": ["Fashion Sneaker Collection", "Casual Slip-Ons"]
    }
    event = "Customer mentions shopping for a birthday gift"
    
    response = engine.generate_response("GIFTING", context, event)
    print(f"Response:\n{response}\n")


def test_trend_state():
    """Test the TREND conversation state."""
    print("\n" + "="*80)
    print("TEST 4: TREND State")
    print("="*80)
    
    engine = SalesConversationEngine()
    context = {
        "customer_name": "Alex",
        "trend": "retro 90s sneaker styles",
        "products": ["Vintage Court Shoes", "Retro Basketball High-Tops"],
        "lifestyle": "urban streetwear enthusiast"
    }
    event = "Customer asks about trendy sneaker styles"
    
    response = engine.generate_response("TREND", context, event)
    print(f"Response:\n{response}\n")


def test_checkout_state():
    """Test the CHECKOUT conversation state."""
    print("\n" + "="*80)
    print("TEST 5: CHECKOUT State")
    print("="*80)
    
    engine = SalesConversationEngine()
    context = {
        "customer_name": "David",
        "product_name": "Running Shoes Pro",
        "price": "$120",
        "size": "10.5",
        "loyalty_points": "250 points earned"
    }
    event = "Customer ready to complete purchase"
    
    response = engine.generate_response("CHECKOUT", context, event)
    print(f"Response:\n{response}\n")


def test_failure_payment():
    """Test the FAILURE state with payment issue."""
    print("\n" + "="*80)
    print("TEST 6: FAILURE State (Payment Issue)")
    print("="*80)
    
    engine = SalesConversationEngine()
    context = {
        "customer_name": "Emily",
        "error_type": "PAYMENT_FAILED",
        "product_name": "Classic Leather Sneaker"
    }
    event = "Payment declined during checkout"
    
    response = engine.generate_response("FAILURE", context, event)
    print(f"Response:\n{response}\n")


def test_failure_inventory():
    """Test the FAILURE state with inventory issue."""
    print("\n" + "="*80)
    print("TEST 7: FAILURE State (Inventory Issue)")
    print("="*80)
    
    engine = SalesConversationEngine()
    context = {
        "customer_name": "Tom",
        "error_type": "OUT_OF_STOCK",
        "product_name": "Limited Edition High-Tops",
        "alternative_products": ["Classic High-Tops", "Premium Court Shoes"]
    }
    event = "Requested size out of stock"
    
    response = engine.generate_response("FAILURE", context, event)
    print(f"Response:\n{response}\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SALES CONVERSATION LAYER - TEST SUITE")
    print("="*80)
    print("\nTesting all conversation states with the Groq LLM integration...")
    print("Note: If GROQ_API_KEY is not set, fallback templates will be used.\n")
    
    try:
        test_discovery_state()
        test_comparison_state()
        test_gifting_state()
        test_trend_state()
        test_checkout_state()
        test_failure_payment()
        test_failure_inventory()
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED")
        print("="*80)
        print("\nIf you see template-like responses, the fallback system is working.")
        print("If you see natural, personalized responses, the Groq LLM is working.")
        print("\nTo use Groq LLM:")
        print("  1. Set GROQ_API_KEY environment variable")
        print("  2. Set GROQ_MODEL environment variable (e.g., 'mixtral-8x7b-32768')")
        print("     Or set GROQ_MODEL_LIST with comma-separated models for fallback")
        print("\nPowerShell example:")
        print("  $env:GROQ_API_KEY = 'your-api-key'")
        print("  $env:GROQ_MODEL = 'mixtral-8x7b-32768'")
        print("  py test_conversation_layer.py\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
