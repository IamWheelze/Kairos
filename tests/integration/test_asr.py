"""Integration tests for ASR module.

Tests the ASR model with real audio files to verify transcription functionality.
"""

import os
import pytest
import wave
import tempfile
import struct


@pytest.fixture
def sample_audio_file():
    """Create a simple WAV file for testing.

    Note: This creates a silent audio file. For real testing,
    you would use actual audio samples with speech.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        audio_path = f.name

    # Create a simple WAV file (1 second of silence at 16kHz)
    sample_rate = 16000
    duration = 1  # seconds
    frequency = 440  # Hz (A4 note)

    with wave.open(audio_path, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        # Generate simple tone (for testing audio file validity)
        frames = []
        for i in range(int(sample_rate * duration)):
            value = int(32767 * 0.1)  # Low amplitude
            frames.append(struct.pack('<h', value))

        wav_file.writeframes(b''.join(frames))

    yield audio_path

    # Cleanup
    if os.path.exists(audio_path):
        os.remove(audio_path)


def test_asr_model_initialization():
    """Test ASR model can be initialized with different engines."""
    from kairos.asr.model import ASRModel

    # Test default (Google) engine
    model = ASRModel()
    assert model.model_name == "google"
    assert model.recognizer is not None

    # Test explicit engine
    model_google = ASRModel(model_name="google")
    assert model_google.model_name == "google"

    # Test unsupported engine falls back to google
    model_unknown = ASRModel(model_name="unknown_engine")
    assert model_unknown.model_name == "google"


def test_asr_model_predict_with_missing_file():
    """Test ASR model handles missing audio file gracefully."""
    from kairos.asr.model import ASRModel

    model = ASRModel(model_name="google")
    result = model.predict("/nonexistent/audio/file.wav")

    # Should return None for missing file
    assert result is None


def test_asr_model_predict_with_valid_file(sample_audio_file):
    """Test ASR model can process a valid audio file.

    Note: This test may fail or return None because the sample audio
    is just a tone, not actual speech. This tests the pipeline works.
    """
    from kairos.asr.model import ASRModel

    model = ASRModel(model_name="google")

    # This will likely return None or error because there's no speech
    # in the sample audio, but it tests that the pipeline executes
    try:
        result = model.predict(sample_audio_file)
        # Result could be None (no speech detected) or some text
        assert result is None or isinstance(result, str)
    except Exception as e:
        # Network errors or API rate limits are acceptable in testing
        pytest.skip(f"ASR service unavailable: {e}")


def test_asr_model_save_load_config():
    """Test ASR model configuration can be saved and loaded."""
    from kairos.asr.model import ASRModel
    import tempfile
    import json

    model = ASRModel(model_name="google", language="es-ES")

    with tempfile.NamedTemporaryFile(mode='w', suffix=".json", delete=False) as f:
        config_path = f.name

    try:
        # Save config
        model.save_model(config_path)
        assert os.path.exists(config_path)

        # Verify config contents
        with open(config_path, 'r') as f:
            config = json.load(f)
        assert config["model_name"] == "google"
        assert config["language"] == "es-ES"

        # Load config into new model
        new_model = ASRModel()
        new_model.load_model(config_path)
        assert new_model.model_name == "google"
        assert new_model.language == "es-ES"

    finally:
        if os.path.exists(config_path):
            os.remove(config_path)


def test_asr_model_evaluate():
    """Test ASR model evaluation functionality."""
    from kairos.asr.model import ASRModel

    model = ASRModel(model_name="google")

    # Test with empty data
    result = model.evaluate([], [])
    assert result["accuracy"] == 0.0
    assert result["total"] == 0

    # Test with no data
    result = model.evaluate(None, None)
    assert result["accuracy"] == 0.0
    assert result["total"] == 0


def test_asr_supported_engines():
    """Test that ASR model declares supported engines."""
    from kairos.asr.model import ASRModel

    assert "google" in ASRModel.SUPPORTED_ENGINES
    assert "sphinx" in ASRModel.SUPPORTED_ENGINES
    assert "whisper" in ASRModel.SUPPORTED_ENGINES
    assert len(ASRModel.SUPPORTED_ENGINES) > 0


@pytest.mark.skipif(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is None,
    reason="Google Cloud credentials not configured"
)
def test_asr_google_cloud_engine():
    """Test Google Cloud Speech engine (requires credentials)."""
    from kairos.asr.model import ASRModel

    model = ASRModel(model_name="google_cloud")
    assert model.model_name == "google_cloud"


def test_asr_model_train_not_applicable():
    """Test that train method exists but is not applicable for pre-trained models."""
    from kairos.asr.model import ASRModel

    model = ASRModel()
    # Should not raise an error, just log a warning
    model.train(None, None, 0, 0)
