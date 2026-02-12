"""
Persuasion Engine for Sales Agent

Implements memory-aware conversational AI with:
- Automatic conversation summarization
- Context building from session metadata
- Persuasive prompt injection for better sales responses

NO AI frameworks required - uses simple keyword matching and context building.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_conversation_summary(chat_context: List[Dict[str, Any]]) -> str:
    """
    Generate a concise 2-3 line conversation summary.
    
    Uses simple heuristics to identify:
    - Customer interests (products mentioned)
    - Buying stage (browsing, comparing, ready to buy)
    - Last action taken
    
    Args:
        chat_context: List of message objects with sender, message, timestamp
        
    Returns:
        2-3 line summary string
    """
    if not chat_context or len(chat_context) < 2:
        return ""
    
    # Take last 10 messages for summary
    recent_messages = chat_context[-10:]
    
    # Extract key information
    user_messages = [msg["message"].lower() for msg in recent_messages if msg.get("sender") == "user"]
    agent_messages = [msg["message"].lower() for msg in recent_messages if msg.get("sender") == "agent"]
    
    if not user_messages:
        return ""
    
    # Detect products/categories mentioned
    product_keywords = ["shoe", "shirt", "pant", "jacket", "sneaker", "tshirt", "jeans", "hoodie", "running", "casual", "formal"]
    mentioned_products = []
    for msg in user_messages:
        for keyword in product_keywords:
            if keyword in msg:
                if keyword not in mentioned_products:
                    mentioned_products.append(keyword)
    
    # Detect buying stage
    purchase_intent_keywords = ["buy", "purchase", "order", "checkout", "cart", "payment"]
    browsing_keywords = ["show", "recommend", "looking", "want", "need", "find"]
    comparing_keywords = ["compare", "difference", "between", "better", "cheaper", "vs"]
    
    stage = "browsing"
    for msg in user_messages[-3:]:  # Check last 3 user messages
        if any(kw in msg for kw in purchase_intent_keywords):
            stage = "ready to purchase"
            break
        elif any(kw in msg for kw in comparing_keywords):
            stage = "comparing options"
        elif any(kw in msg for kw in browsing_keywords) and stage == "browsing":
            stage = "exploring products"
    
    # Build summary
    product_text = ""
    if mentioned_products:
        if len(mentioned_products) == 1:
            product_text = f"{mentioned_products[0]}s"
        elif len(mentioned_products) == 2:
            product_text = f"{mentioned_products[0]}s and {mentioned_products[1]}s"
        else:
            product_text = f"{', '.join(mentioned_products[:-1])}s and {mentioned_products[-1]}s"
    else:
        product_text = "products"
    
    # Check cart status from agent messages
    cart_status = ""
    for msg in agent_messages[-3:]:
        if "added to cart" in msg or "cart" in msg:
            cart_status = " Items added to cart."
            break
    
    summary = f"Customer is {stage} - interested in {product_text}.{cart_status} {len(user_messages)} interactions so far."
    
    logger.info(f"📝 Generated summary: {summary}")
    return summary


def build_persuasive_context(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract key context from session metadata for persuasive responses.
    
    Returns structured context including:
    - last_action: What customer did last
    - last_recommended_skus: Products shown previously
    - cart: Current cart items
    - conversation_summary: Condensed interaction history
    - channels: Which channels customer used
    
    Args:
        metadata: Session metadata dict
        
    Returns:
        Structured context dict
    """
    context = {
        "last_action": metadata.get("last_action"),
        "last_recommended_skus": metadata.get("last_recommended_skus", []),
        "cart": metadata.get("cart", []),
        "conversation_summary": metadata.get("conversation_summary", ""),
        "channels": metadata.get("channels", []),
        "recent_products": metadata.get("recent", []),
        "has_previous_context": bool(metadata.get("conversation_summary"))
    }
    
    logger.debug(f"🧠 Built persuasive context: {context}")
    return context


def inject_memory_into_prompt(base_prompt: str, metadata: Dict[str, Any], is_restoration: bool = False) -> str:
    """
    Enhance the base prompt with memory and context.
    
    Appends structured context to help the agent:
    - Reference past interactions naturally
    - Suggest complementary items
    - Ask relevant follow-up questions
    - Sound persuasive but natural
    
    Args:
        base_prompt: Original system/user prompt
        metadata: Session metadata with conversation history
        is_restoration: True if this is a session restore (use summary)
        
    Returns:
        Enhanced prompt with memory context
    """
    context = build_persuasive_context(metadata)
    
    # Skip if no meaningful context
    if not any([
        context["last_action"],
        context["last_recommended_skus"],
        context["cart"],
        context["conversation_summary"]
    ]):
        return base_prompt
    
    memory_section = "\n\n--- CUSTOMER MEMORY (USE THIS TO BE HELPFUL) ---\n"
    
    # Add conversation summary if available
    if context["conversation_summary"]:
        memory_section += f"\nPrevious Interaction Summary:\n{context['conversation_summary']}\n"
    
    # Add last action context
    if context["last_action"]:
        action_hints = {
            "purchase_intent": "Customer showed buying interest - encourage completion",
            "cart_update": "Customer added items - suggest checkout or complementary products",
            "browsing": "Customer is exploring - show relevant options and ask preferences"
        }
        hint = action_hints.get(context["last_action"], "Continue the conversation naturally")
        memory_section += f"\nLast Action: {context['last_action']} ({hint})\n"
    
    # Add recently viewed/recommended products
    if context["last_recommended_skus"]:
        sku_list = ", ".join(context["last_recommended_skus"][:5])  # Limit to 5
        memory_section += f"\nRecently Recommended: SKUs {sku_list}\n"
        memory_section += "If relevant, reference these products naturally.\n"
    
    # Add cart information
    if context["cart"]:
        cart_count = len(context["cart"])
        memory_section += f"\nCart Status: {cart_count} item(s) in cart\n"
        memory_section += "Encourage checkout or suggest complementary items.\n"
    
    # Add persuasive rules
    memory_section += "\n--- RESPONSE RULES ---\n"
    memory_section += "1. Reference past interactions naturally (don't say 'I remember', just use the context)\n"
    memory_section += "2. Ask one relevant follow-up question to keep engagement\n"
    memory_section += "3. If cart has items, gently encourage checkout\n"
    memory_section += "4. Suggest complementary products when appropriate\n"
    memory_section += "5. Sound helpful and consultative, not pushy\n"
    memory_section += "6. Use customer's preferences from summary to personalize\n"
    
    # For session restoration, add special instruction
    if is_restoration and context["conversation_summary"]:
        memory_section += "\n🔄 SESSION RESTORED: Begin response by acknowledging previous conversation naturally.\n"
        memory_section += "Example: 'You were looking at [products] earlier. Would you like to continue?'\n"
    
    memory_section += "--- END MEMORY ---\n\n"
    
    enhanced_prompt = base_prompt + memory_section
    
    logger.debug(f"💡 Injected memory into prompt ({len(memory_section)} chars)")
    return enhanced_prompt


def should_generate_summary(chat_context: List[Dict[str, Any]]) -> bool:
    """
    Check if it's time to generate a conversation summary.
    
    Triggers every 6 messages (3 user + 3 agent turns).
    
    Args:
        chat_context: Full chat history
        
    Returns:
        True if summary should be generated
    """
    if not chat_context:
        return False
    
    # Generate summary every 6 messages
    return len(chat_context) % 6 == 0 and len(chat_context) >= 6


def extract_skus_from_cards(cards: List[Dict[str, Any]]) -> List[str]:
    """
    Extract product SKUs from card objects returned by workers.
    
    Args:
        cards: List of card dictionaries (usually product cards)
        
    Returns:
        List of SKU strings
    """
    skus = []
    for card in cards:
        if isinstance(card, dict):
            # Try different possible SKU fields
            sku = card.get("sku") or card.get("SKU") or card.get("product_id")
            if sku:
                skus.append(str(sku))
    
    logger.debug(f"🏷️  Extracted {len(skus)} SKUs from {len(cards)} cards")
    return skus


def detect_last_action(message: str) -> Optional[str]:
    """
    Detect user intent from message using simple keyword matching.
    
    No AI required - uses predefined keyword patterns.
    
    Args:
        message: User message text
        
    Returns:
        Action type string or None
    """
    message_lower = message.lower()
    
    # Purchase intent keywords
    if any(kw in message_lower for kw in ["buy", "purchase", "checkout", "order", "payment", "pay"]):
        return "purchase_intent"
    
    # Cart update keywords
    if any(kw in message_lower for kw in ["add to cart", "add cart", "cart"]):
        return "cart_update"
    
    # Browsing keywords
    if any(kw in message_lower for kw in ["show", "recommend", "looking", "want", "need", "find", "search"]):
        return "browsing"
    
    return None


def format_summary_banner(summary: str) -> Dict[str, Any]:
    """
    Format conversation summary as a banner for UI display.
    
    Used in kiosk/website channels to show previous interaction context.
    
    Args:
        summary: Conversation summary text
        
    Returns:
        Banner object dict for frontend
    """
    return {
        "type": "summary_banner",
        "title": "Previous Interaction",
        "message": summary,
        "icon": "history",
        "dismissible": True
    }
