"""Lightweight intent recognition for common presentation commands.

Returns a tuple (intent_name, params_dict) or None when unknown.
"""

import re
from typing import Optional, Tuple, Dict


from kairos.logging import get_logger


class IntentProcessor:
    def __init__(self):
        # Placeholder for future extensibility
        self.log = get_logger("kairos.nlp.intent")

    def recognize_intent(self, user_input: str) -> Optional[Tuple[str, Dict]]:
        text = (user_input or "").strip().lower()
        if not text:
            return None

        if "next" in text:
            return ("next_slide", {})
        if "previous" in text or "back" in text:
            return ("previous_slide", {})
        if text.startswith("start presentation") or text.startswith("start slideshow"):
            return ("start_presentation", {})
        if text.startswith("stop presentation") or text.startswith("end presentation"):
            return ("stop_presentation", {})
        if "list presentations" in text or "show presentations" in text:
            return ("list_presentations", {})
        if "current slide" in text or "what slide" in text:
            return ("current_slide", {})

        m = re.search(r"go to slide\s+(\d+)|slide\s+(\d+)", text)
        if m:
            num = m.group(1) or m.group(2)
            try:
                slide_number = int(num)
                self.log.debug("Parsed slide number: %s", slide_number)
                return ("set_slide", {"slide_number": slide_number})
            except ValueError:
                return None

        return None


# Backward compatible alias
IntentRecognizer = IntentProcessor
