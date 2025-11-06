# core.py

import os
from typing import Optional
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
        client: Optional[PresentationAPIClient] = None
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
        """Process a text command through NLP and presentation control.

        Args:
            command: Text command string

        Returns:
            Result dictionary from presentation controller
        """
        self.log.info("Processing command: %s", command)
        intent_tuple = self.nlp_processor.recognize_intent(command)
        return self.presentation_controller.execute_intent(intent_tuple)

    def process_audio_file(self, audio_file_path):
        """Process an audio file through the complete voice pipeline.

        Audio → ASR → NLP → Presentation Control

        Args:
            audio_file_path: Path to audio file (WAV format)

        Returns:
            Dictionary with transcription, intent, and execution result
        """
        if not self._running:
            self.log.error("System not started. Call start() first.")
            return {
                "ok": False,
                "error": "System not running"
            }

        self.log.info("Processing audio file: %s", audio_file_path)

        # Step 1: Transcribe audio to text (ASR)
        transcription = self.asr_model.predict(audio_file_path)
        if not transcription:
            self.log.warning("No transcription from audio file")
            return {
                "ok": False,
                "error": "Speech recognition failed or no speech detected",
                "transcription": None
            }

        self.log.info("Transcription: '%s'", transcription)

        # Step 2: Recognize intent (NLP)
        intent_tuple = self.nlp_processor.recognize_intent(transcription)
        if not intent_tuple:
            self.log.warning("No intent recognized from: '%s'", transcription)
            return {
                "ok": False,
                "error": "Intent not recognized",
                "transcription": transcription,
                "intent": None
            }

        intent_name, params = intent_tuple
        self.log.info("Intent recognized: %s with params: %s", intent_name, params)

        # Step 3: Execute presentation control
        result = self.presentation_controller.execute_intent(intent_tuple)

        return {
            "ok": result.get("ok", False),
            "transcription": transcription,
            "intent": intent_name,
            "params": params,
            "result": result
        }

    def process_voice_command_interactive(self, duration=5):
        """Record audio from microphone and process through the voice pipeline.

        Audio Recording → ASR → NLP → Presentation Control

        Args:
            duration: Recording duration in seconds (default: 5)

        Returns:
            Dictionary with transcription, intent, and execution result
        """
        if not self._running:
            self.log.error("System not started. Call start() first.")
            return {
                "ok": False,
                "error": "System not running"
            }

        import time
        import threading

        self.log.info("Starting voice command recording for %d seconds...", duration)

        # Use a list to capture frames in the thread
        recorded_frames = []
        recording_complete = threading.Event()

        def record_for_duration():
            try:
                from pyaudio import PyAudio, paInt16

                audio = PyAudio()
                stream = audio.open(
                    format=paInt16,
                    channels=self.audio_recorder.channels,
                    rate=self.audio_recorder.rate,
                    input=True,
                    frames_per_buffer=self.audio_recorder.chunk,
                )

                # Record for specified duration
                frames_needed = int(self.audio_recorder.rate / self.audio_recorder.chunk * duration)
                for _ in range(frames_needed):
                    data = stream.read(self.audio_recorder.chunk, exception_on_overflow=False)
                    recorded_frames.append(data)

                stream.stop_stream()
                stream.close()
                audio.terminate()

            except Exception as e:
                self.log.error("Recording error: %s", e)
            finally:
                recording_complete.set()

        # Start recording in background thread
        record_thread = threading.Thread(target=record_for_duration)
        record_thread.start()

        # Wait for recording to complete
        recording_complete.wait(timeout=duration + 2)

        if not recorded_frames:
            self.log.error("No audio recorded")
            return {
                "ok": False,
                "error": "Audio recording failed"
            }

        # Save recorded audio to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_audio_path = f.name

        try:
            self.audio_recorder.stop_recording(recorded_frames)
            # The recorder saves to its configured filename, so we need to move it
            import shutil
            if os.path.exists(self.audio_recorder.filename):
                shutil.move(self.audio_recorder.filename, temp_audio_path)

            self.log.info("Audio recorded to: %s", temp_audio_path)

            # Process the recorded audio file
            return self.process_audio_file(temp_audio_path)

        finally:
            # Cleanup temp file
            import os
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

    def start(self, config_path: Optional[str] = None):
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
