"""End-to-end integration tests for the complete voice pipeline.

Tests the full flow: Audio → ASR → NLP → Presentation Control
"""

import os
import pytest
import tempfile
import wave
import struct


@pytest.fixture
def sample_audio_with_speech():
    """Create a sample WAV file (placeholder for testing).

    Note: This creates a simple audio file. In real testing, you would
    use actual recorded speech samples.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        audio_path = f.name

    # Create a simple WAV file (1 second at 16kHz)
    sample_rate = 16000
    duration = 1

    with wave.open(audio_path, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        # Generate simple audio signal
        frames = []
        for i in range(int(sample_rate * duration)):
            value = int(32767 * 0.3)  # Medium amplitude
            frames.append(struct.pack('<h', value))

        wav_file.writeframes(b''.join(frames))

    yield audio_path

    # Cleanup
    if os.path.exists(audio_path):
        os.remove(audio_path)


@pytest.fixture
def kairos_system():
    """Create and start a Kairos system instance for testing."""
    from kairos.core import Kairos

    system = Kairos()
    system.start()

    yield system

    system.stop()


def test_kairos_initialization():
    """Test that Kairos system can be initialized and started."""
    from kairos.core import Kairos

    system = Kairos()
    assert system.get_status() == "stopped"

    system.start()
    assert system.get_status() == "running"
    assert system.audio_recorder is not None
    assert system.asr_model is not None
    assert system.nlp_processor is not None
    assert system.presentation_controller is not None

    system.stop()
    assert system.get_status() == "stopped"


def test_text_command_processing(kairos_system):
    """Test processing text commands through NLP → Presentation."""
    # Test next slide command
    result = kairos_system.process_command("next slide")
    assert result is not None
    assert result.get("ok") is True
    assert result.get("command") == "next_slide"

    # Test previous slide command
    result = kairos_system.process_command("previous slide")
    assert result.get("ok") is True
    assert result.get("command") == "previous_slide"

    # Test jump to slide command
    result = kairos_system.process_command("go to slide 5")
    assert result.get("ok") is True
    assert result.get("command") == "set_slide"

    # Test unknown command
    result = kairos_system.process_command("do a backflip")
    assert result.get("ok") is False


def test_intent_recognition_pipeline(kairos_system):
    """Test NLP intent recognition with various commands."""
    test_cases = [
        ("next slide", "next_slide"),
        ("previous slide", "previous_slide"),
        ("go to slide 10", "set_slide"),
        ("start presentation", "start_presentation"),
        ("stop presentation", "stop_presentation"),
        ("list presentations", "list_presentations"),
        ("what's the current slide", "current_slide"),
    ]

    for command, expected_intent in test_cases:
        intent_tuple = kairos_system.nlp_processor.recognize_intent(command)
        assert intent_tuple is not None
        intent_name, params = intent_tuple
        assert intent_name == expected_intent


def test_audio_file_processing_pipeline(kairos_system, sample_audio_with_speech):
    """Test processing an audio file through the complete pipeline.

    Note: This test may not produce a valid transcription since the audio
    is synthetic, but it tests that the pipeline executes without errors.
    """
    result = kairos_system.process_audio_file(sample_audio_with_speech)

    assert result is not None
    assert "transcription" in result

    # The transcription might be None (no speech) or a string
    # Either is acceptable for synthetic audio
    transcription = result.get("transcription")
    assert transcription is None or isinstance(transcription, str)


def test_audio_file_processing_with_nonexistent_file(kairos_system):
    """Test that processing a nonexistent audio file fails gracefully."""
    result = kairos_system.process_audio_file("/nonexistent/audio.wav")

    assert result is not None
    assert result.get("ok") is False
    assert "error" in result


def test_audio_processing_when_system_stopped():
    """Test that audio processing requires system to be started."""
    from kairos.core import Kairos

    system = Kairos()
    # Don't start the system

    result = system.process_audio_file("/some/file.wav")
    assert result.get("ok") is False
    assert "not running" in result.get("error", "").lower()


def test_configuration_loading(kairos_system):
    """Test that configuration is loaded and components are configured."""
    assert kairos_system.config is not None
    assert isinstance(kairos_system.config, dict)

    # Check components are configured
    assert kairos_system.audio_recorder.rate in [16000, 44100, 48000]
    assert kairos_system.audio_recorder.channels in [1, 2]


def test_nlp_to_presentation_integration(kairos_system):
    """Test NLP → Presentation Controller integration."""
    # Recognize an intent
    intent_tuple = kairos_system.nlp_processor.recognize_intent("next slide")
    assert intent_tuple is not None

    # Execute the intent
    result = kairos_system.presentation_controller.execute_intent(intent_tuple)
    assert result.get("ok") is True
    assert result.get("command") == "next_slide"


def test_multiple_commands_in_sequence(kairos_system):
    """Test processing multiple commands in sequence."""
    commands = [
        "next slide",
        "next slide",
        "previous slide",
        "go to slide 3",
        "next slide",
    ]

    for command in commands:
        result = kairos_system.process_command(command)
        assert result is not None
        assert result.get("ok") is True


def test_error_handling_for_malformed_intent(kairos_system):
    """Test error handling for commands that don't map to intents."""
    result = kairos_system.process_command("invalid gibberish xyz123")

    # Should handle gracefully
    assert result is not None
    # Might return error or unknown intent
    assert isinstance(result, dict)


@pytest.mark.skipif(
    os.getenv('CI') == 'true',
    reason="Skipping microphone tests in CI environment"
)
def test_voice_command_interactive_without_microphone():
    """Test that interactive voice command handles missing microphone gracefully."""
    from kairos.core import Kairos

    system = Kairos()
    system.start()

    try:
        # This will likely fail without a microphone, but should not crash
        result = system.process_voice_command_interactive(duration=1)
        # Either succeeds or fails gracefully
        assert result is not None
        assert "ok" in result or "error" in result
    except Exception as e:
        # Exception is acceptable if no microphone is available
        assert "audio" in str(e).lower() or "pyaudio" in str(e).lower()
    finally:
        system.stop()


def test_full_pipeline_components_initialized(kairos_system):
    """Test that all pipeline components are properly initialized."""
    # Audio recorder
    assert kairos_system.audio_recorder is not None
    assert hasattr(kairos_system.audio_recorder, 'start_recording')
    assert hasattr(kairos_system.audio_recorder, 'stop_recording')

    # ASR model
    assert kairos_system.asr_model is not None
    assert hasattr(kairos_system.asr_model, 'predict')
    assert kairos_system.asr_model.model_name in ['google', 'sphinx', 'whisper']

    # NLP processor
    assert kairos_system.nlp_processor is not None
    assert hasattr(kairos_system.nlp_processor, 'recognize_intent')

    # Presentation controller
    assert kairos_system.presentation_controller is not None
    assert hasattr(kairos_system.presentation_controller, 'execute_intent')
    assert hasattr(kairos_system.presentation_controller, 'next_slide')
    assert hasattr(kairos_system.presentation_controller, 'previous_slide')


def test_logging_throughout_pipeline(kairos_system):
    """Test that logging is configured for all components."""
    # Each component should have a logger
    assert hasattr(kairos_system, 'log')
    assert hasattr(kairos_system.audio_recorder, 'log')
    assert hasattr(kairos_system.asr_model, 'log')
    assert hasattr(kairos_system.nlp_processor, 'log')
    assert hasattr(kairos_system.presentation_controller, 'log')
