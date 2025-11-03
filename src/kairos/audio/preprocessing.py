# This file contains functions for preprocessing audio data, such as normalization and segmentation.

import numpy as np
import librosa

def normalize_audio(audio, target_db=-20):
    """Normalize audio to a target decibel level."""
    audio_db = librosa.amplitude_to_db(np.abs(audio))
    normalization_factor = target_db - np.mean(audio_db)
    normalized_audio = audio * (10 ** (normalization_factor / 20))
    return normalized_audio

def segment_audio(audio, segment_length=2.0, sample_rate=22050):
    """Segment audio into chunks of specified length."""
    segment_samples = int(segment_length * sample_rate)
    segments = [audio[i:i + segment_samples] for i in range(0, len(audio), segment_samples) if len(audio[i:i + segment_samples]) == segment_samples]
    return segments

def trim_silence(audio, top_db=20):
    """Trim silence from the beginning and end of the audio."""
    return librosa.effects.trim(audio, top_db=top_db)[0]