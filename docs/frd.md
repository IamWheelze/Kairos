# Kairos Voice-Activated Presentation System — Functional Requirements Document (FRD)

## 1. Introduction
Kairos enables hands-free control of presentation software using voice commands by combining audio capture, automatic speech recognition (ASR), natural language processing (NLP), and a presentation control adapter.

## 2. Scope
- In scope: capturing audio, transcribing commands, recognizing intents, controlling presentation software (e.g., ProPresenter via network API), and providing basic status feedback.
- Out of scope: full slide authoring, cloud training pipelines, advanced multi-speaker diarization, and enterprise-grade authentication.

## 3. Stakeholders
- Presenters and operators, technical support staff, and developers maintaining Kairos.

## 4. Definitions
- ASR: Automatic Speech Recognition converting audio to text.
- NLP: Natural Language Processing mapping text to intents.
- Intent: A high-level action requested by the user (e.g., next slide).

## 5. Assumptions & Constraints
- A working microphone is available.
- Presentation software exposes a controllable API (e.g., ProPresenter Network API) reachable on the local network.
- Initial operation targets English commands; extensibility for other locales is planned.

## 6. Functional Requirements
- FR1 Start/Stop System: User can start and stop the Kairos service via CLI.
- FR2 Status: User can query whether the system is running.
- FR3 Audio Capture: System captures microphone input at a configurable sample rate.
- FR4 Transcription: System transcribes audio into text using a pluggable ASR model.
- FR5 Intent Recognition: System maps transcribed text to high-level intents.
- FR6 Next/Previous Slide: System advances or reverses slides via presentation API.
- FR7 Jump to Slide: System jumps to a specific slide number on command.
- FR8 Start/Stop Presentation: System starts or stops a presentation by identifier.
- FR9 List Presentations: System fetches available presentations.
- FR10 Current Slide: System queries current slide information.
- FR11 Error Handling: System reports actionable errors for unsupported commands or API failures.
- FR12 Configuration: System supports configuration of audio params, ASR model, and API host/port.

## 7. Non-Functional Requirements
- NFR1 Reliability: System should not crash on malformed inputs; graceful degradation with clear messages.
- NFR2 Extensibility: New intents and presentation backends can be added with minimal changes.
- NFR3 Observability: Log key events (start/stop, recognized intents, API calls, errors).
- NFR4 Performance: Command latency should be acceptable for live use (<1s for local intents when possible).
- NFR5 Portability: Runs on standard Windows/macOS environments with Python 3.8+.

## 8. User Interactions (Examples)
- “Start presentation Alpha” → Start/Stop Presentation (FR8)
- “Next slide” / “Previous slide” → Slide control (FR6)
- “Go to slide 12” → Jump to Slide (FR7)
- “What’s the current slide?” → Current Slide (FR10)

## 9. Success Criteria
- Core commands (FR6–FR10) operate reliably against a supported presentation API.
- CLI controls (FR1–FR2) and basic configuration (FR12) function correctly.

