"""OpenAI NLP Provider.

Uses GPT-3.5-turbo or GPT-4o for intelligent intent recognition.
Requires OpenAI API key. Pay-as-you-go pricing.
"""

import json
from typing import Optional, Tuple, Dict
from kairos.logging import get_logger
from .provider_base import NLPProvider


class OpenAIProvider(NLPProvider):
    """OpenAI GPT-based intent recognition."""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    }

    SUPPORTED_INTENTS = [
        "next_slide",
        "previous_slide",
        "set_slide",
        "start_presentation",
        "stop_presentation",
        "list_presentations",
        "current_slide",
    ]

    def __init__(self, config: Optional[Dict] = None):
        """Initialize OpenAI provider.

        Args:
            config: Configuration with 'api_key' and optional 'model'
        """
        super().__init__(config)
        self.log = get_logger("kairos.nlp.openai")
        self.model = self.config.get("model", "gpt-3.5-turbo")
        self.api_key = self.config.get("api_key")

        # Validate model
        if self.model not in self.PRICING:
            self.log.warning("Unknown model %s, defaulting to gpt-3.5-turbo", self.model)
            self.model = "gpt-3.5-turbo"

    def recognize_intent(self, text: str) -> Optional[Tuple[str, Dict]]:
        """Recognize intent using OpenAI GPT.

        Args:
            text: User input text

        Returns:
            Tuple of (intent_name, params_dict) or None
        """
        if not text:
            return None

        if not self.api_key:
            self.log.error("OpenAI API key not configured")
            return None

        try:
            import openai
        except ImportError:
            self.log.error("openai package not installed. Run: pip install openai")
            return None

        try:
            client = openai.OpenAI(api_key=self.api_key)

            system_prompt = f"""You are an intent classifier for a presentation control system.

Analyze the user's command and respond with a JSON object containing:
- "intent": one of {self.SUPPORTED_INTENTS}
- "params": dictionary with any parameters (e.g., {{"slide_number": 5}})

If no intent matches, return: {{"intent": null, "params": {{}}}}

Examples:
User: "next slide please"
Response: {{"intent": "next_slide", "params": {{}}}}

User: "go to slide 10"
Response: {{"intent": "set_slide", "params": {{"slide_number": 10}}}}

User: "what's the weather?"
Response: {{"intent": null, "params": {{}}}}

Only respond with the JSON object, nothing else."""

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.0,  # Deterministic
                max_tokens=100,
            )

            result_text = response.choices[0].message.content.strip()
            self.log.debug("OpenAI response: %s", result_text)

            # Parse JSON response
            result = json.loads(result_text)
            intent = result.get("intent")
            params = result.get("params", {})

            if intent and intent in self.SUPPORTED_INTENTS:
                self.log.info("Recognized intent: %s with params: %s", intent, params)
                return (intent, params)
            else:
                self.log.warning("No intent recognized from: %s", text)
                return None

        except json.JSONDecodeError as e:
            self.log.error("Failed to parse OpenAI response: %s", e)
            return None
        except Exception as e:
            self.log.error("OpenAI API error: %s", e)
            return None

    def get_provider_name(self) -> str:
        """Get provider name."""
        return f"openai-{self.model}"

    def get_cost_per_request(self) -> float:
        """Estimate cost per request in USD.

        Assumes ~100 input tokens + ~50 output tokens per request.
        """
        pricing = self.PRICING.get(self.model, self.PRICING["gpt-3.5-turbo"])
        input_cost = (100 / 1_000_000) * pricing["input"]
        output_cost = (50 / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def requires_api_key(self) -> bool:
        """Check if API key required (yes)."""
        return True

    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """Validate OpenAI configuration."""
        if not self.api_key:
            return False, "OpenAI API key is required"

        # Check if openai package is installed
        try:
            import openai
        except ImportError:
            return False, "openai package not installed. Run: pip install openai"

        return True, None
