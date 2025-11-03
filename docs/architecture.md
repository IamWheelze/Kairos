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
- **Purpose**: Converts spoken language into text.
- **Key Files**:
  - `model.py`: Defines the architecture of the ASR model.
  - `infer.py`: Runs inference on audio data to produce text output.

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
1. **Audio Input**: The user speaks into the microphone, and the audio is recorded by the `recorder.py`.
2. **Audio Processing**: The recorded audio is preprocessed using functions in `preprocessing.py`.
3. **Speech Recognition**: The preprocessed audio is fed into the ASR model defined in `model.py`, and the output text is generated via `infer.py`.
4. **Intent Recognition**: The generated text is analyzed by the NLP module to determine the user's intent using `intent.py`.
5. **Presentation Control**: Based on the recognized intent, commands are sent to the presentation software through `controller.py`.

## Conclusion
The Kairos architecture is designed to be flexible and scalable, allowing for enhancements and new features to be integrated easily. Each module is responsible for a specific aspect of the system, promoting clean separation of concerns and maintainability.