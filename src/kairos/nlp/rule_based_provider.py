"""Rule-Based NLP Provider.

Simple, fast, and FREE intent recognition using pattern matching.
No AI APIs required.
"""

import re
from typing import Optional, Tuple, Dict
from kairos.logging import get_logger
from .provider_base import NLPProvider


class RuleBasedProvider(NLPProvider):
    """Rule-based intent recognition using regex patterns."""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize rule-based provider.

        Args:
            config: Optional configuration (not used for rule-based)
        """
        super().__init__(config)
        self.log = get_logger("kairos.nlp.rule_based")

    def recognize_intent(self, text: str) -> Optional[Tuple[str, Dict]]:
        """Recognize intent using pattern matching.

        Args:
            text: User input text

        Returns:
            Tuple of (intent_name, params_dict) or None
        """
        if not text:
            return None

        text = text.strip().lower()

        # Next slide
        if any(word in text for word in ["next", "forward", "advance"]):
            return ("next_slide", {})

        # Previous slide
        if any(word in text for word in ["previous", "back", "prior", "last"]):
            return ("previous_slide", {})

        # Start presentation
        if "start" in text and ("presentation" in text or "slideshow" in text):
            return ("start_presentation", {})

        # Stop presentation
        if ("stop" in text or "end" in text) and ("presentation" in text or "slideshow" in text):
            return ("stop_presentation", {})

        # List presentations
        if "list" in text and ("presentation" in text or "slideshow" in text):
            return ("list_presentations", {})

        # Current slide
        if "current" in text and "slide" in text:
            return ("current_slide", {})
        if "what slide" in text or "which slide" in text:
            return ("current_slide", {})

        # Go to slide number
        patterns = [
            r"go\s+to\s+slide\s+(\d+)",
            r"slide\s+(\d+)",
            r"jump\s+to\s+(\d+)",
            r"show\s+slide\s+(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    slide_number = int(match.group(1))
                    self.log.debug("Parsed slide number: %s", slide_number)
                    return ("set_slide", {"slide_number": slide_number})
                except ValueError:
                    continue

        return None

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "rule-based"

    def get_cost_per_request(self) -> float:
        """Get cost per request (free)."""
        return 0.0

    def requires_api_key(self) -> bool:
        """Check if API key required (no)."""
        return False
