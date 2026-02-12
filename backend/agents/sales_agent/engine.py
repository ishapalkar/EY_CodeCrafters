"""Conversation + Sales Psychology + Personalization layer.

Responsibilities:
- Tone control, persuasion, trust building, emotional framing, sales language.
- Uses Groq LLM when available; falls back to safe templates otherwise.
- Memory-aware: Injects conversation context and persuasive rules.
- Never raises uncaught exceptions; always returns a human-readable string.

Demo:
    SalesConversationEngine().generate_response(
        state="DISCOVERY",
        context={"product_name": "Reebok Winter Jacket", "budget": "mid", "occasion": "office"},
        session_metadata={"conversation_summary": "...", "last_action": "browsing"}
    )
"""
from typing import Dict, Any, Optional
import os
import logging

from groq import Groq

from .prompts import get_system_prompt
from .rules import PERSUASION_RULES, SAFETY_RULES
from .dialog_templates import render_template
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


STATE_TEMPERATURE = {
    "DISCOVERY": 0.6,
    "COMPARISON": 0.5,
    "GIFTING": 0.7,
    "TREND": 0.8,
    "CHECKOUT": 0.3,
    "FAILURE": 0.2,
}


MODEL_NAME = "llama-3.1-8b-instant"


class SalesConversationEngine:
    def __init__(self):
        self._client: Optional[Groq] = None

    def _get_client(self) -> Optional[Groq]:
        if self._client is not None:
            return self._client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return None
        try:
            self._client = Groq(api_key=api_key)
            return self._client
        except Exception:
            return None

    def _build_messages(self, state: str, context: Dict[str, Any], event: str, session_metadata: Optional[Dict[str, Any]] = None) -> list:
        system_prompt = get_system_prompt(state)
        
        # Inject memory context if available
        if session_metadata:
            try:
                from persuasion_engine import inject_memory_into_prompt
                is_restoration = session_metadata.get("has_summary", False)
                system_prompt = inject_memory_into_prompt(system_prompt, session_metadata, is_restoration)
                logger.debug("🧠 Memory context injected into prompt")
            except Exception as mem_error:
                logger.warning(f"⚠️ Failed to inject memory: {mem_error}")
        
        rules_block = "\n".join([
            "Persuasion rules:" , *PERSUASION_RULES,
            "Safety rules:", *SAFETY_RULES,
            "Remember: trust first, no hallucinated prices/policies, no upsell in FAILURE or CHECKOUT."
        ])
        user_block = {
            "state": state,
            "event": event,
            "context": context,
        }
        return [
            {"role": "system", "content": f"{system_prompt}\n\n{rules_block}"},
            {"role": "user", "content": str(user_block)},
        ]

    def generate_response(self, state: str, context: Dict[str, Any], event: str = "NONE", session_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response; never raise. Falls back to safe template on failure.
        
        Args:
            state: Current conversation state (DISCOVERY, COMPARISON, etc.)
            context: Context dict with product info, user prefs, etc.
            event: Event trigger for state transition
            session_metadata: Session data for memory-aware responses (conversation_summary, last_action, etc.)
        
        Returns:
            Generated response string
        """
        try:
            temperature = STATE_TEMPERATURE.get(state, 0.4)
            client = self._get_client()
            if not client:
                return render_template(state, context)

            messages = self._build_messages(state, context, event, session_metadata)
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                temperature=temperature,
                messages=messages,
                max_tokens=420,
            )
            content = completion.choices[0].message.content.strip()
            return content or render_template(state, context)
        except Exception as e:
            logger.warning(f"⚠️ LLM generation failed: {e}")
            return render_template(state, context)


__all__ = ["SalesConversationEngine"]
