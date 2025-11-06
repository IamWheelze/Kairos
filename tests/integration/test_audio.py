"""Integration tests for audio recording module.

Tests audio capture and recording functionality.
"""

import os
import pytest
import tempfile
import wave


@pytest.fixture
def temp_audio_file():
    """Create a temporary file path for audio recording."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        audio_path = f.name

    yield audio_path

    # Cleanup
    if os.path.exists(audio_path):
        os.remove(audio_path)


def test_audio_recorder_initialization():
    """Test AudioRecorder can be initialized with default parameters."""
    from kairos.audio.recorder import AudioRecorder

    recorder = AudioRecorder()
    assert recorder.filename == "output.wav"
    assert recorder.channels == 1
    assert recorder.rate == 44100
    assert recorder.chunk == 1024


def test_audio_recorder_custom_initialization(temp_audio_file):
    """Test AudioRecorder can be initialized with custom parameters."""
    from kairos.audio.recorder import AudioRecorder

    recorder = AudioRecorder(
        filename=temp_audio_file,
        channels=2,
        rate=16000,
        chunk=512
    )

    assert recorder.filename == temp_audio_file
    assert recorder.channels == 2
    assert recorder.rate == 16000
    assert recorder.chunk == 512


def test_audio_recorder_stop_with_empty_frames(temp_audio_file):
    """Test stopping recording with no frames (edge case)."""
    from kairos.audio.recorder import AudioRecorder

    recorder = AudioRecorder(filename=temp_audio_file)

    # Stop recording with empty frames
    frames = []
    recorder.stop_recording(frames)

    # File should be created even if empty
    assert os.path.exists(temp_audio_file)

    # Verify it's a valid WAV file
    with wave.open(temp_audio_file, 'rb') as wf:
        assert wf.getnchannels() == 1
        assert wf.getframerate() == 44100


def test_audio_recorder_stop_with_sample_frames(temp_audio_file):
    """Test stopping recording with sample audio frames."""
    from kairos.audio.recorder import AudioRecorder
    import struct

    recorder = AudioRecorder(filename=temp_audio_file, rate=16000)

    # Create some sample audio frames (1 second of silence)
    frames = []
    samples_per_frame = recorder.chunk
    num_frames = recorder.rate // samples_per_frame  # 1 second

    for _ in range(num_frames):
        frame_data = struct.pack('<' + 'h' * samples_per_frame, *([0] * samples_per_frame))
        frames.append(frame_data)

    # Stop recording
    recorder.stop_recording(frames)

    # Verify file was created
    assert os.path.exists(temp_audio_file)

    # Verify WAV file properties
    with wave.open(temp_audio_file, 'rb') as wf:
        assert wf.getnchannels() == 1
        assert wf.getframerate() == 16000
        assert wf.getnframes() > 0


@pytest.mark.skipif(
    not hasattr(os, 'environ') or os.environ.get('CI') == 'true',
    reason="Skipping PyAudio tests in CI environment (no audio devices)"
)
def test_audio_recorder_ensure_pyaudio():
    """Test that PyAudio can be imported (requires PyAudio installed)."""
    from kairos.audio.recorder import AudioRecorder

    recorder = AudioRecorder()

    try:
        pa_tuple = recorder._ensure_pa()
        assert pa_tuple is not None
        assert len(pa_tuple) == 2
    except RuntimeError as e:
        # Expected if PyAudio is not installed
        assert "PyAudio is required" in str(e)


def test_audio_preprocessing_exists():
    """Test that audio preprocessing module exists and can be imported."""
    try:
        from kairos.audio import preprocessing
        assert preprocessing is not None
    except ImportError:
        pytest.skip("Audio preprocessing module not yet implemented")


def test_audio_package_initialization():
    """Test that audio package can be imported."""
    from kairos import audio
    assert audio is not None

    from kairos.audio.recorder import AudioRecorder
    assert AudioRecorder is not None


def test_audio_recorder_logging():
    """Test that AudioRecorder has logging configured."""
    from kairos.audio.recorder import AudioRecorder

    recorder = AudioRecorder()
    assert recorder.log is not None
    assert hasattr(recorder.log, 'info')
    assert hasattr(recorder.log, 'error')
    assert hasattr(recorder.log, 'warning')


def test_multiple_audio_recorders(temp_audio_file):
    """Test that multiple AudioRecorder instances can coexist."""
    from kairos.audio.recorder import AudioRecorder

    recorder1 = AudioRecorder(filename=temp_audio_file, rate=16000)
    recorder2 = AudioRecorder(filename="other.wav", rate=44100)

    assert recorder1.rate == 16000
    assert recorder2.rate == 44100
    assert recorder1.filename != recorder2.filename
