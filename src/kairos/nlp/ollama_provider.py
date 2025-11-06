"""Ollama NLP Provider.

Uses local AI models via Ollama (LLaMA, Mistral, etc.)
100% FREE, runs on your computer, no API keys needed.
Requires Ollama to be installed: https://ollama.ai
"""

import json
from typing import Optional, Tuple, Dict
from kairos.logging import get_logger
from .provider_base import NLPProvider


class OllamaProvider(NLPProvider):
    """Ollama local AI intent recognition."""

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
        """Initialize Ollama provider.

        Args:
            config: Configuration with optional 'model' and 'base_url'
        """
        super().__init__(config)
        self.log = get_logger("kairos.nlp.ollama")
        self.model = self.config.get("model", "llama3.2")
        self.base_url = self.config.get("base_url", "http://localhost:11434")

    def recognize_intent(self, text: str) -> Optional[Tuple[str, Dict]]:
        """Recognize intent using local Ollama model.

        Args:
            text: User input text

        Returns:
            Tuple of (intent_name, params_dict) or None
        """
        if not text:
            return None

        try:
            import requests
        except ImportError:
            self.log.error("requests package not installed. Run: pip install requests")
            return None

        try:
            system_prompt = f"""You are an intent classifier for a presentation control system.

Analyze the user's command and respond with ONLY a JSON object containing:
- "intent": one of {self.SUPPORTED_INTENTS}
- "params": dictionary with any parameters (e.g., {{"slide_number": 5}})

If no intent matches, return: {{"intent": null, "params": {{}}}}

Examples:
User: "next slide please"
{{"intent": "next_slide", "params": {{}}}}

User: "go to slide 10"
{{"intent": "set_slide", "params": {{"slide_number": 10}}}}

Respond ONLY with the JSON object."""

            payload = {
                "model": self.model,
                "prompt": f"{system_prompt}\n\nUser: {text}\nResponse:",
                "stream": False,
                "format": "json",
            }

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                self.log.error("Ollama API error: %s", response.text)
                return None

            result_data = response.json()
            result_text = result_data.get("response", "").strip()
            self.log.debug("Ollama response: %s", result_text)

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
            self.log.error("Failed to parse Ollama response: %s", e)
            return None
        except requests.exceptions.ConnectionError:
            self.log.error("Cannot connect to Ollama at %s. Is Ollama running?", self.base_url)
            return None
        except Exception as e:
            self.log.error("Ollama API error: %s", e)
            return None

    def get_provider_name(self) -> str:
        """Get provider name."""
        return f"ollama-{self.model}"

    def get_cost_per_request(self) -> float:
        """Get cost per request (free)."""
        return 0.0

    def requires_api_key(self) -> bool:
        """Check if API key required (no)."""
        return False

    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """Validate Ollama configuration."""
        try:
            import requests
        except ImportError:
            return False, "requests package not installed. Run: pip install requests"

        # Check if Ollama is running
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return True, None
            else:
                return False, f"Ollama server returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, f"Cannot connect to Ollama at {self.base_url}. Install from https://ollama.ai"
        except Exception as e:
            return False, f"Ollama validation error: {str(e)}"
