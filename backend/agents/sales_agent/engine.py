"""Conversation + Sales Psychology + Personalization layer.

Responsibilities:
- Tone control, persuasion, trust building, emotional framing, sales language.
- Uses Groq LLM when available; falls back to safe templates otherwise.
- Never raises uncaught exceptions; always returns a human-readable string.

Demo:
    SalesConversationEngine().generate_response(
        state="DISCOVERY",
        context={"product_name": "Reebok Winter Jacket", "budget": "mid", "occasion": "office"}
    )
"""
from typing import Dict, Any, Optional
import os

from groq import Groq

from .prompts import get_system_prompt
from .rules import PERSUASION_RULES, SAFETY_RULES
from .dialog_templates import render_template
from dotenv import load_dotenv
load_dotenv()


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

    def _build_messages(self, state: str, context: Dict[str, Any], event: str) -> list:
        system_prompt = get_system_prompt(state)
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

    def generate_response(self, state: str, context: Dict[str, Any], event: str = "NONE") -> str:
        """Generate a response; never raise. Falls back to safe template on failure."""
        try:
            temperature = STATE_TEMPERATURE.get(state, 0.4)
            client = self._get_client()
            if not client:
                return render_template(state, context)

            messages = self._build_messages(state, context, event)
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                temperature=temperature,
                messages=messages,
                max_tokens=420,
            )
            content = completion.choices[0].message.content.strip()
            return content or render_template(state, context)
        except Exception:
            return render_template(state, context)


__all__ = ["SalesConversationEngine"]
