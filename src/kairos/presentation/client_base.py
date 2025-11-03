from abc import ABC, abstractmethod


class PresentationAPIClient(ABC):
    @abstractmethod
    def send_command(self, command: str, presentation_id=None, *args):
        """Send a command to the presentation backend.

        Returns a JSON-serializable object describing the result.
        """
        raise NotImplementedError

