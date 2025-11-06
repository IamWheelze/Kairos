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
        self.bible_service = None
        self._running = False
        self.config = {}
        self.log = get_logger("kairos.core")
        self.current_bible_verse = None  # Track current verse for next/previous
        self.current_bible_translation = "KJV"  # Default translation

    def initialize_components(self):
        from kairos.audio.recorder import AudioRecorder
        from kairos.asr.model import ASRModel
        from kairos.nlp.intent import IntentProcessor
        from kairos.presentation.controller import PresentationController
        from kairos.presentation.http_client import HTTPPresentationClient
        from kairos.presentation.client_base import PresentationAPIClient
        from kairos.bible.service import BibleService

        audio_cfg = self.config.get("audio", {})
        asr_cfg = self.config.get("asr", {})
        bible_cfg = self.config.get("bible", {})

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

        # Initialize Bible service
        self.bible_service = BibleService(
            api=bible_cfg.get("api", BibleService.BIBLE_API_COM),
            default_translation=bible_cfg.get("translation", "KJV")
        )
        self.current_bible_translation = bible_cfg.get("translation", "KJV")

    def run(self):
        # Backwards-compatible entry point
        self.start()
        print("Kairos system is running. Awaiting voice commands...")

    def process_command(self, command):
        """Process a text command through NLP and presentation control.

        Args:
            command: Text command string

        Returns:
            Result dictionary from presentation controller or Bible service
        """
        self.log.info("Processing command: %s", command)
        intent_tuple = self.nlp_processor.recognize_intent(command)

        if not intent_tuple:
            return {"ok": False, "error": "No intent recognized"}

        intent_name, params = intent_tuple

        # Handle Bible-specific intents
        if intent_name == "show_bible_verse":
            return self.show_bible_verse(params.get("reference"))
        elif intent_name == "set_bible_translation":
            return self.set_bible_translation(params.get("translation"))
        elif intent_name == "next_verse":
            return self.next_bible_verse()
        elif intent_name == "previous_verse":
            return self.previous_bible_verse()

        # Handle presentation intents
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

    # Bible Command Handlers

    def show_bible_verse(self, reference: str) -> dict:
        """Fetch and display a Bible verse.

        Args:
            reference: Bible reference (e.g., "John 3:16")

        Returns:
            Dictionary with verse information
        """
        if not self.bible_service or not self.bible_service.is_available():
            return {
                "ok": False,
                "error": "Bible service not available. Install 'requests' package."
            }

        if not reference:
            return {
                "ok": False,
                "error": "No Bible reference provided"
            }

        self.log.info("Fetching Bible verse: %s (%s)", reference, self.current_bible_translation)

        verse = self.bible_service.get_verse(reference, self.current_bible_translation)

        if not verse:
            return {
                "ok": False,
                "error": f"Could not find Bible verse: {reference}",
                "reference": reference
            }

        # Store current verse for next/previous navigation
        self.current_bible_verse = verse

        return {
            "ok": True,
            "command": "show_bible_verse",
            "reference": verse.reference,
            "text": verse.text,
            "translation": verse.translation,
            "verse_data": verse.to_dict()
        }

    def set_bible_translation(self, translation: str) -> dict:
        """Set the Bible translation.

        Args:
            translation: Translation abbreviation (e.g., "ESV", "NIV")

        Returns:
            Dictionary with success status
        """
        if not translation:
            return {
                "ok": False,
                "error": "No translation specified"
            }

        translation = translation.upper()
        self.current_bible_translation = translation
        self.log.info("Bible translation set to: %s", translation)

        return {
            "ok": True,
            "command": "set_bible_translation",
            "translation": translation,
            "message": f"Bible translation changed to {translation}"
        }

    def next_bible_verse(self) -> dict:
        """Show the next Bible verse.

        Returns:
            Dictionary with verse information
        """
        if not self.current_bible_verse:
            return {
                "ok": False,
                "error": "No current verse. Please show a verse first."
            }

        # Parse current reference and increment
        parsed = self.bible_service.parse_reference(self.current_bible_verse.reference)
        if not parsed:
            return {
                "ok": False,
                "error": "Cannot parse current reference"
            }

        book, chapter, verse, end_verse = parsed
        next_verse = (end_verse or verse) + 1
        next_reference = f"{book} {chapter}:{next_verse}"

        return self.show_bible_verse(next_reference)

    def previous_bible_verse(self) -> dict:
        """Show the previous Bible verse.

        Returns:
            Dictionary with verse information
        """
        if not self.current_bible_verse:
            return {
                "ok": False,
                "error": "No current verse. Please show a verse first."
            }

        # Parse current reference and decrement
        parsed = self.bible_service.parse_reference(self.current_bible_verse.reference)
        if not parsed:
            return {
                "ok": False,
                "error": "Cannot parse current reference"
            }

        book, chapter, verse, _ = parsed
        if verse <= 1:
            return {
                "ok": False,
                "error": "Already at first verse of chapter"
            }

        prev_verse = verse - 1
        prev_reference = f"{book} {chapter}:{prev_verse}"

        return self.show_bible_verse(prev_reference)

if __name__ == "__main__":
    kairos_system = Kairos()
    kairos_system.run()
