# Architecture of the Kairos Voice-Activated Presentation System

## Overview
The Kairos project is designed to create a Voice-Activated Presentation System that leverages automatic speech recognition (ASR) and natural language processing (NLP) to facilitate seamless interaction with presentation software. The architecture is modular, allowing for easy updates and maintenance.

## Components

### 1. Audio Module
- **Purpose**: Handles all audio-related functionalities.
- **Key Files**:
  - `recorder.py`: Captures audio input from the microphone.
  - `preprocessing.py`: Preprocesses audio data for further analysis.

### 2. ASR Module
- **Purpose**: Converts spoken language into text using the SpeechRecognition library.
- **Key Files**:
  - `model.py`: Implements the ASR model with pluggable recognition engines (Google, Sphinx, Whisper, etc.).
  - `infer.py`: Alternative torch-based inference implementation (experimental).
- **Supported Engines**:
  - Google Speech Recognition (default, free tier)
  - CMU Sphinx (offline)
  - Google Cloud Speech (requires credentials)
  - OpenAI Whisper (requires whisper package)
  - Wit.ai (requires API key)

### 3. NLP Module
- **Purpose**: Processes the text output from the ASR module to understand user intents.
- **Key Files**:
  - `intent.py`: Maps recognized commands to specific actions within the presentation system.

### 4. Presentation Module
- **Purpose**: Controls the presentation software based on user commands.
- **Key Files**:
  - `controller.py`: Sends commands to the ProPresenter Network API to manage presentations.

### 5. Training Module
- **Purpose**: Facilitates the training of AI models using prepared datasets.
- **Key Files**:
  - `trainer.py`: Contains the logic for training models and managing training processes.

## Data Flow
1. **Audio Input**: The user speaks into the microphone, and the audio is recorded by `recorder.py`.
2. **Audio Processing** (Optional): The recorded audio can be preprocessed using functions in `preprocessing.py`:
   - `normalize_audio()`: Normalize to target dB level
   - `trim_silence()`: Remove silence from beginning/end
   - `segment_audio()`: Split into chunks
   - `load_audio_file()`: Load and resample audio files
3. **Speech Recognition**: The audio is transcribed to text using the ASR model (`model.py:ASRModel.predict()`), which uses the SpeechRecognition library with pluggable engines.
4. **Intent Recognition**: The transcribed text is analyzed by the NLP module (`intent.py:IntentProcessor.recognize_intent()`) to determine the user's intent:
   - Next/Previous slide
   - Jump to specific slide
   - Start/Stop presentation
   - List presentations
   - Query current slide
5. **Presentation Control**: Based on the recognized intent, commands are sent to the presentation software through `controller.py` via configured API clients:
   - HTTP Client: Communicates with ProPresenter Network API
   - Stub Client: For testing without actual presentation software

## Complete Pipeline Methods

The Kairos core (`src/kairos/core.py`) provides two end-to-end pipeline methods:

### 1. Process Audio File
```python
result = kairos.process_audio_file(audio_file_path)
```
Process a pre-recorded audio file through the complete pipeline: Audio → ASR → NLP → Control.

### 2. Interactive Voice Command
```python
result = kairos.process_voice_command_interactive(duration=5)
```
Record audio from microphone for specified duration and process through the complete pipeline.

Both methods return a dictionary containing:
- `transcription`: The recognized text
- `intent`: The identified intent name
- `params`: Intent parameters (e.g., slide number)
- `result`: Execution result from presentation controller
- `ok`: Success/failure status

## Error Handling (FR11)

Comprehensive error handling is implemented throughout:
- **Configuration**: Validates YAML files, handles missing configs gracefully
- **Audio Processing**: Checks for empty audio, non-finite values, file not found
- **ASR Model**: Handles missing libraries, network errors, API failures
- **HTTP Client**: Timeout handling, HTTP errors, malformed responses
- **Logging**: All modules use structured logging with appropriate levels

## Configuration (FR12)

Configuration is loaded from YAML files with the following precedence:
1. `configs/default.yaml` (base configuration)
2. File specified via `--config` CLI argument
3. File specified via `KAIROS_CONFIG` environment variable

Configuration sections:
- `audio`: Sample rate, channels, chunk size
- `asr`: Model/engine selection, language
- `nlp`: Intent recognition settings
- `presentation`: API client type, HTTP settings, routes

## Conclusion
The Kairos architecture is designed to be flexible and scalable, allowing for enhancements and new features to be integrated easily. Each module is responsible for a specific aspect of the system, promoting clean separation of concerns and maintainability. All functional requirements from the FRD (FR1-FR12) are fully implemented with comprehensive test coverage.