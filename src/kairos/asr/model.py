"""ASR Model for speech-to-text transcription.

Uses the SpeechRecognition library with pluggable recognizer engines.
Supports Google Speech Recognition (default), Sphinx, and other backends.
"""

import os
from typing import Optional, Union
from kairos.logging import get_logger


class ASRModel:
    """Automatic Speech Recognition model using speech_recognition library."""

    SUPPORTED_ENGINES = ["google", "sphinx", "google_cloud", "wit", "azure", "whisper"]

    def __init__(self, model_name: str = "google", input_shape=None, language: str = "en-US"):
        """Initialize ASR model.

        Args:
            model_name: Recognition engine to use (google, sphinx, whisper, etc.)
            input_shape: Not used, kept for backward compatibility
            language: Language code for recognition (default: en-US)
        """
        self.model_name = model_name.lower()
        self.input_shape = input_shape
        self.language = language
        self.log = get_logger("kairos.asr.model")

        if self.model_name not in self.SUPPORTED_ENGINES:
            self.log.warning(
                "Unknown engine '%s', falling back to 'google'. Supported: %s",
                self.model_name,
                self.SUPPORTED_ENGINES
            )
            self.model_name = "google"

        self.recognizer = None
        self.model = self.build_model()
        self.log.info("ASR model initialized with engine: %s", self.model_name)

    def build_model(self):
        """Build/initialize the speech recognition model."""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()

            # Adjust recognizer settings for better accuracy
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8

            self.log.debug("Speech recognizer built successfully")
            return self.recognizer
        except ImportError as e:
            self.log.error("SpeechRecognition library not installed: %s", e)
            raise RuntimeError(
                "SpeechRecognition library is required. Install with: pip install SpeechRecognition"
            ) from e

    def predict(self, audio_input: Union[str, bytes]) -> Optional[str]:
        """Transcribe audio to text.

        Args:
            audio_input: Path to audio file (WAV format) or audio data bytes

        Returns:
            Transcribed text or None if recognition failed
        """
        if self.recognizer is None:
            self.log.error("Recognizer not initialized")
            return None

        try:
            import speech_recognition as sr

            # Handle file path input
            if isinstance(audio_input, str):
                if not os.path.exists(audio_input):
                    self.log.error("Audio file not found: %s", audio_input)
                    return None

                with sr.AudioFile(audio_input) as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = self.recognizer.record(source)
            else:
                # Handle bytes input
                audio_data = sr.AudioData(audio_input, 16000, 2)

            # Perform recognition based on selected engine
            text = self._recognize_with_engine(audio_data)

            if text:
                self.log.info("Transcription successful: '%s'", text)
            else:
                self.log.warning("No speech detected or recognition failed")

            return text

        except Exception as e:
            self.log.error("Error during transcription: %s", e)
            return None

    def _recognize_with_engine(self, audio_data) -> Optional[str]:
        """Perform recognition using the configured engine.

        Args:
            audio_data: AudioData object from speech_recognition

        Returns:
            Recognized text or None
        """
        try:
            if self.model_name == "google":
                # Google Speech Recognition (free tier, no API key needed)
                return self.recognizer.recognize_google(audio_data, language=self.language)

            elif self.model_name == "sphinx":
                # CMU Sphinx (offline)
                return self.recognizer.recognize_sphinx(audio_data)

            elif self.model_name == "google_cloud":
                # Google Cloud Speech (requires credentials)
                credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                return self.recognizer.recognize_google_cloud(
                    audio_data,
                    credentials_json=credentials_json,
                    language=self.language
                )

            elif self.model_name == "wit":
                # Wit.ai (requires API key)
                wit_key = os.getenv("WIT_AI_KEY")
                if wit_key:
                    return self.recognizer.recognize_wit(audio_data, key=wit_key)
                else:
                    self.log.error("WIT_AI_KEY environment variable not set")
                    return None

            elif self.model_name == "whisper":
                # OpenAI Whisper (requires whisper package)
                return self.recognizer.recognize_whisper(audio_data, language=self.language.split("-")[0])

            else:
                self.log.error("Unsupported engine: %s", self.model_name)
                return None

        except Exception as e:
            self.log.error("Recognition failed with %s engine: %s", self.model_name, e)
            return None

    def train(self, training_data, labels, epochs, batch_size):
        """Train the ASR model.

        Note: SpeechRecognition uses pre-trained models, so training is not applicable.
        This method is kept for API compatibility.
        """
        self.log.warning(
            "Training not applicable for SpeechRecognition library. "
            "The library uses pre-trained cloud/offline models."
        )
        pass

    def evaluate(self, test_data, test_labels):
        """Evaluate the ASR model.

        Args:
            test_data: List of audio file paths
            test_labels: List of expected transcriptions

        Returns:
            Dictionary with evaluation metrics
        """
        if not test_data or not test_labels:
            self.log.warning("No test data provided for evaluation")
            return {"accuracy": 0.0, "total": 0}

        correct = 0
        total = len(test_data)

        for audio_path, expected_text in zip(test_data, test_labels):
            predicted_text = self.predict(audio_path)
            if predicted_text and predicted_text.lower() == expected_text.lower():
                correct += 1

        accuracy = correct / total if total > 0 else 0.0
        self.log.info("Evaluation complete: %d/%d correct (%.2f%%)", correct, total, accuracy * 100)

        return {
            "accuracy": accuracy,
            "correct": correct,
            "total": total
        }

    def save_model(self, filepath):
        """Save model configuration.

        Note: SpeechRecognition models are cloud-based or pre-installed,
        so we only save the configuration.
        """
        import json

        config = {
            "model_name": self.model_name,
            "language": self.language,
        }

        try:
            with open(filepath, 'w') as f:
                json.dump(config, f, indent=2)
            self.log.info("Model configuration saved to %s", filepath)
        except Exception as e:
            self.log.error("Failed to save model config: %s", e)

    def load_model(self, filepath):
        """Load model configuration.

        Args:
            filepath: Path to configuration JSON file
        """
        import json

        try:
            with open(filepath, 'r') as f:
                config = json.load(f)

            self.model_name = config.get("model_name", "google")
            self.language = config.get("language", "en-US")

            # Rebuild with new config
            self.model = self.build_model()
            self.log.info("Model configuration loaded from %s", filepath)

        except Exception as e:
            self.log.error("Failed to load model config: %s", e)
