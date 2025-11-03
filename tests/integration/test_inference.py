import pytest
from kairos.asr.infer import run_inference
from kairos.audio.preprocess import preprocess_audio

def test_inference_with_valid_audio():
    audio_path = "tests/resources/test_audio.wav"
    processed_audio = preprocess_audio(audio_path)
    result = run_inference(processed_audio)
    assert result is not None
    assert isinstance(result, dict)
    assert "transcription" in result

def test_inference_with_invalid_audio():
    audio_path = "tests/resources/invalid_audio.wav"
    processed_audio = preprocess_audio(audio_path)
    result = run_inference(processed_audio)
    assert result is None

def test_inference_performance():
    audio_path = "tests/resources/test_audio.wav"
    processed_audio = preprocess_audio(audio_path)
    
    import time
    start_time = time.time()
    run_inference(processed_audio)
    end_time = time.time()
    
    assert (end_time - start_time) < 2  # Inference should be under 2 seconds