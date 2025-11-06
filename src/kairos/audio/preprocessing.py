"""Audio preprocessing functions for normalization, segmentation, and silence removal.

This module contains utility functions for preprocessing audio data before
passing it to the ASR model.
"""

import numpy as np
from typing import List, Tuple, Optional
from kairos.logging import get_logger

log = get_logger("kairos.audio.preprocessing")


def normalize_audio(audio: np.ndarray, target_db: float = -20) -> Optional[np.ndarray]:
    """Normalize audio to a target decibel level.

    Args:
        audio: Audio signal as numpy array
        target_db: Target decibel level (default: -20)

    Returns:
        Normalized audio array or None if normalization fails
    """
    try:
        import librosa

        if audio is None or len(audio) == 0:
            log.warning("Empty audio provided for normalization")
            return None

        audio_db = librosa.amplitude_to_db(np.abs(audio))
        mean_db = np.mean(audio_db)

        if not np.isfinite(mean_db):
            log.warning("Non-finite mean dB value, returning original audio")
            return audio

        normalization_factor = target_db - mean_db
        normalized_audio = audio * (10 ** (normalization_factor / 20))

        log.debug("Audio normalized from %.2f dB to %.2f dB", mean_db, target_db)
        return normalized_audio

    except ImportError as e:
        log.error("librosa not installed: %s", e)
        return None
    except Exception as e:
        log.error("Error normalizing audio: %s", e)
        return None


def segment_audio(
    audio: np.ndarray,
    segment_length: float = 2.0,
    sample_rate: int = 22050,
    allow_partial: bool = False
) -> List[np.ndarray]:
    """Segment audio into chunks of specified length.

    Args:
        audio: Audio signal as numpy array
        segment_length: Length of each segment in seconds (default: 2.0)
        sample_rate: Sample rate of the audio (default: 22050)
        allow_partial: If True, include partial segments at the end (default: False)

    Returns:
        List of audio segments
    """
    try:
        if audio is None or len(audio) == 0:
            log.warning("Empty audio provided for segmentation")
            return []

        segment_samples = int(segment_length * sample_rate)

        if segment_samples <= 0:
            log.error("Invalid segment length: %f seconds", segment_length)
            return []

        segments = []
        for i in range(0, len(audio), segment_samples):
            segment = audio[i:i + segment_samples]

            if len(segment) == segment_samples:
                segments.append(segment)
            elif allow_partial and len(segment) > 0:
                segments.append(segment)

        log.debug(
            "Segmented audio into %d segments of %.2f seconds",
            len(segments),
            segment_length
        )
        return segments

    except Exception as e:
        log.error("Error segmenting audio: %s", e)
        return []


def trim_silence(
    audio: np.ndarray,
    top_db: float = 20,
    frame_length: int = 2048,
    hop_length: int = 512
) -> Optional[Tuple[np.ndarray, Tuple[int, int]]]:
    """Trim silence from the beginning and end of the audio.

    Args:
        audio: Audio signal as numpy array
        top_db: Threshold in decibels below reference to consider as silence
        frame_length: Length of frames for silence detection
        hop_length: Number of samples between frames

    Returns:
        Tuple of (trimmed_audio, (start_index, end_index)) or None if error
    """
    try:
        import librosa

        if audio is None or len(audio) == 0:
            log.warning("Empty audio provided for silence trimming")
            return None

        trimmed, indices = librosa.effects.trim(
            audio,
            top_db=top_db,
            frame_length=frame_length,
            hop_length=hop_length
        )

        original_duration = len(audio) / 22050  # Assume 22050 sample rate
        trimmed_duration = len(trimmed) / 22050

        log.debug(
            "Trimmed silence: %.2fs -> %.2fs (%.1f%% retained)",
            original_duration,
            trimmed_duration,
            100 * trimmed_duration / original_duration if original_duration > 0 else 0
        )

        return trimmed, indices

    except ImportError as e:
        log.error("librosa not installed: %s", e)
        return None
    except Exception as e:
        log.error("Error trimming silence: %s", e)
        return None


def load_audio_file(file_path: str, sample_rate: int = 22050) -> Optional[Tuple[np.ndarray, int]]:
    """Load an audio file and optionally resample it.

    Args:
        file_path: Path to the audio file
        sample_rate: Target sample rate (default: 22050, None for native rate)

    Returns:
        Tuple of (audio_data, sample_rate) or None if loading fails
    """
    try:
        import librosa
        import os

        if not os.path.exists(file_path):
            log.error("Audio file not found: %s", file_path)
            return None

        audio, sr = librosa.load(file_path, sr=sample_rate)
        log.info("Loaded audio file: %s (%.2fs, %d Hz)", file_path, len(audio) / sr, sr)

        return audio, sr

    except ImportError as e:
        log.error("librosa not installed: %s", e)
        return None
    except Exception as e:
        log.error("Error loading audio file %s: %s", file_path, e)
        return None