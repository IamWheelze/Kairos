"""NLP Provider Base Class.

Abstract interface for different NLP/AI providers to recognize intents
from transcribed text.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict


class NLPProvider(ABC):
    """Abstract base class for NLP providers."""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize the NLP provider.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

    @abstractmethod
    def recognize_intent(self, text: str) -> Optional[Tuple[str, Dict]]:
        """Recognize intent from text.

        Args:
            text: User input text

        Returns:
            Tuple of (intent_name, params_dict) or None if no intent recognized
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this provider.

        Returns:
            Provider name (e.g., "rule-based", "gpt-3.5", "gpt-4o")
        """
        pass

    @abstractmethod
    def get_cost_per_request(self) -> float:
        """Get estimated cost per request in USD.

        Returns:
            Cost in USD (0.0 for free providers)
        """
        pass

    @abstractmethod
    def requires_api_key(self) -> bool:
        """Check if this provider requires an API key.

        Returns:
            True if API key is required
        """
        pass

    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """Validate the provider configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.requires_api_key():
            api_key = self.config.get("api_key")
            if not api_key:
                return False, "API key is required but not provided"
        return True, None
