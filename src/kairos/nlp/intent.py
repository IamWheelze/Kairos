"""Intent recognition with multiple AI provider support.

Supports:
- Rule-based (FREE, fast, no API)
- OpenAI GPT-3.5 (low cost, smart)
- OpenAI GPT-4o (best quality)
- Ollama (FREE, local AI)
"""

from typing import Optional, Tuple, Dict
from kairos.logging import get_logger
from .provider_factory import create_provider, get_available_providers
from .rule_based_provider import RuleBasedProvider


class IntentProcessor:
    """Intent processor with selectable AI providers."""

    def __init__(self, provider_id: str = "rule-based", provider_config: Optional[Dict] = None):
        """Initialize intent processor.

        Args:
            provider_id: Provider to use ("rule-based", "openai-gpt-3.5", "openai-gpt-4o", etc.)
            provider_config: Provider-specific configuration (API keys, etc.)
        """
        self.log = get_logger("kairos.nlp.intent")
        self.provider_id = provider_id
        self.provider_config = provider_config or {}

        # Create provider
        self.provider = create_provider(provider_id, self.provider_config)

        if self.provider is None:
            self.log.warning("Failed to create provider %s, falling back to rule-based", provider_id)
            self.provider = RuleBasedProvider()
            self.provider_id = "rule-based"

        self.log.info(
            "IntentProcessor initialized with %s (cost: $%.4f/request)",
            self.provider_id,
            self.provider.get_cost_per_request()
        )

    def recognize_intent(self, user_input: str) -> Optional[Tuple[str, Dict]]:
        """Recognize intent from user input.

        Args:
            user_input: User's spoken/typed command

        Returns:
            Tuple of (intent_name, params_dict) or None
        """
        return self.provider.recognize_intent(user_input)

    def get_provider_info(self) -> Dict:
        """Get information about the current provider.

        Returns:
            Dictionary with provider metadata
        """
        return {
            "id": self.provider_id,
            "name": self.provider.get_provider_name(),
            "cost_per_request": self.provider.get_cost_per_request(),
            "requires_api_key": self.provider.requires_api_key(),
        }

    def set_provider(self, provider_id: str, provider_config: Optional[Dict] = None) -> bool:
        """Change the AI provider.

        Args:
            provider_id: New provider ID
            provider_config: New provider configuration

        Returns:
            True if successful, False otherwise
        """
        new_provider = create_provider(provider_id, provider_config or {})

        if new_provider is None:
            self.log.error("Failed to create provider: %s", provider_id)
            return False

        self.provider = new_provider
        self.provider_id = provider_id
        self.provider_config = provider_config or {}

        self.log.info("Switched to provider: %s", provider_id)
        return True

    @staticmethod
    def get_available_providers():
        """Get list of available providers.

        Returns:
            List of provider info dictionaries
        """
        return get_available_providers()


# Backward compatible alias
IntentRecognizer = IntentProcessor

