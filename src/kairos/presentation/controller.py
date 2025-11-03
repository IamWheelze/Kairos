"""Presentation control adapter.

Provides methods mirroring typical presentation actions and an execute_intent
helper to route simple (intent, params) tuples.
"""

from kairos.logging import get_logger


class PresentationController:
    def __init__(self, api_client=None):
        # Provide a stub API client if none supplied
        self.api_client = api_client or _StubAPIClient()
        self.log = get_logger("kairos.presentation.controller")

    def start_presentation(self, presentation_id=None):
        """Start the specified presentation."""
        response = self.api_client.send_command("start", presentation_id)
        return response

    def stop_presentation(self, presentation_id=None):
        """Stop the specified presentation."""
        response = self.api_client.send_command("stop", presentation_id)
        return response

    def next_slide(self, presentation_id=None):
        """Advance to the next slide in the presentation."""
        response = self.api_client.send_command("next_slide", presentation_id)
        return response

    def previous_slide(self, presentation_id=None):
        """Go back to the previous slide in the presentation."""
        response = self.api_client.send_command("previous_slide", presentation_id)
        return response

    def get_current_slide(self, presentation_id=None):
        """Retrieve the current slide of the specified presentation."""
        response = self.api_client.send_command("current_slide", presentation_id)
        return response

    def set_slide(self, presentation_id=None, slide_number=1):
        """Set the presentation to a specific slide."""
        response = self.api_client.send_command("set_slide", presentation_id, slide_number)
        return response

    def get_presentations(self):
        """Retrieve a list of available presentations."""
        response = self.api_client.send_command("list_presentations")
        return response

    def is_presentation_running(self, presentation_id=None):
        """Check if the specified presentation is currently running."""
        response = self.api_client.send_command("is_running", presentation_id)
        return response

    def execute_intent(self, intent_tuple, presentation_id=None):
        """Execute an intent returned by NLP recognizer.

        intent_tuple: (name, params_dict) or None
        """
        if not intent_tuple:
            return {"ok": False, "error": "Unknown or no intent"}
        name, params = intent_tuple
        self.log.info("Executing intent=%s params=%s", name, params)
        if name == "next_slide":
            return self.next_slide(presentation_id)
        if name == "previous_slide":
            return self.previous_slide(presentation_id)
        if name == "start_presentation":
            return self.start_presentation(presentation_id)
        if name == "stop_presentation":
            return self.stop_presentation(presentation_id)
        if name == "list_presentations":
            return self.get_presentations()
        if name == "current_slide":
            return self.get_current_slide(presentation_id)
        if name == "set_slide":
            return self.set_slide(presentation_id, params.get("slide_number", 1))
        return {"ok": False, "error": f"Unsupported intent: {name}"}


class _StubAPIClient:
    def send_command(self, command, presentation_id=None, *args):
        # Simple stub response for development
        return {"ok": True, "command": command, "presentation_id": presentation_id, "args": list(args)}
