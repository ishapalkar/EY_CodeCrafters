"""Fallback dialog templates for each state.
These are used when the LLM is unavailable or fails.
"""
from typing import Dict, Any


TEMPLATES = {
    "DISCOVERY": (
        "Got it—you're looking at {product_name} for {occasion}. "
        "I'll keep it simple and recommend what best fits your {budget} budget and style."
    ),
    "COMPARISON": (
        "Between {product_name} and options like {alternatives}, here's the crisp take: "
        "choose what fits your {occasion} need and budget without overthinking."
    ),
    "GIFTING": (
        "For gifting, {product_name} is a thoughtful pick—practical for {occasion} and within budget. "
        "Happy to keep it easy."
    ),
    "TREND": (
        "{product_name} is on-trend right now—great for {occasion} while staying in your {budget} range."
    ),
    "CHECKOUT": (
        "All set to confirm {product_name} at ₹{price}? It matches your {occasion} need. "
        "Tell me if you'd like any last check before proceeding."
    ),
    "FAILURE": (
        "Sorry for the hiccup. I won't push anything—let me know if you want to retry, "
        "see a similar item, or get a quick status update."
    ),
}


def get_template(state: str) -> str:
    return TEMPLATES.get(state, TEMPLATES["DISCOVERY"])


def render_template(state: str, context: Dict[str, Any]) -> str:
    template = get_template(state)
    safe_ctx = {
        "product_name": context.get("product_name", "this option"),
        "price": context.get("price", "the listed price"),
        "category": context.get("category", "item"),
        "budget": context.get("budget", "your"),
        "occasion": context.get("occasion", "everyday"),
        "alternatives": ", ".join(context.get("alternatives", [])) or "other options",
    }
    try:
        return template.format(**safe_ctx)
    except Exception:
        return template
