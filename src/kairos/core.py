# core.py

from kairos.config import load_config
from kairos.logging import get_logger


class Kairos:
    def __init__(self):
        self.audio_recorder = None
        self.asr_model = None
        self.nlp_processor = None
        self.presentation_controller = None
        self._running = False
        self.config = {}
        self.log = get_logger("kairos.core")

    def initialize_components(self):
        from kairos.audio.recorder import AudioRecorder
        from kairos.asr.model import ASRModel
        from kairos.nlp.intent import IntentProcessor
        from kairos.presentation.controller import PresentationController
        from kairos.presentation.http_client import HTTPPresentationClient
        from kairos.presentation.client_base import PresentationAPIClient

        audio_cfg = self.config.get("audio", {})
        asr_cfg = self.config.get("asr", {})

        self.audio_recorder = AudioRecorder(
            filename=audio_cfg.get("filename", "output.wav"),
            channels=audio_cfg.get("channels", 1),
            rate=audio_cfg.get("rate", 44100),
            chunk=audio_cfg.get("chunk", 1024),
        )
        self.asr_model = ASRModel(model_name=asr_cfg.get("model_name", "baseline"))
        self.nlp_processor = IntentProcessor()

        # Build presentation client based on config
        pres_cfg = self.config.get("presentation", {})
        client_type = pres_cfg.get("client", "stub")
        client: PresentationAPIClient | None = None
        if client_type == "http":
            http_cfg = pres_cfg.get("http", {})
            client = HTTPPresentationClient(
                base_url=http_cfg.get("base_url", "http://127.0.0.1:50001"),
                routes=http_cfg.get("routes", {}),
                headers=http_cfg.get("headers", {}),
                timeout=float(http_cfg.get("timeout", 2.0)),
            )

        self.presentation_controller = PresentationController(api_client=client)

    def run(self):
        # Backwards-compatible entry point
        self.start()
        print("Kairos system is running. Awaiting voice commands...")

    def process_command(self, command):
        self.log.info("Processing command: %s", command)
        intent_tuple = self.nlp_processor.recognize_intent(command)
        return self.presentation_controller.execute_intent(intent_tuple)

    def start(self, config_path: str | None = None):
        if not self._running:
            self.config = load_config(config_path)
            self.initialize_components()
            self._running = True
            self.log.info("Kairos started")

    def stop(self):
        self._running = False
        self.log.info("Kairos stopped")

    def get_status(self):
        return "running" if self._running else "stopped"

if __name__ == "__main__":
    kairos_system = Kairos()
    kairos_system.run()
