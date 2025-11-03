# Requirements Traceability Matrix

Linking FRD items to implementation modules and (planned) tests.

| FR | Requirement | Implementation | Tests
|----|-------------|----------------|----------------|
| FR1 | Start/Stop System | `src/kairos/core.py:Kairos.start/stop`, `src/kairos/cli.py` | `tests/unit/test_core_cli.py`
| FR2 | Status | `src/kairos/core.py:get_status`, `src/kairos/cli.py` | `tests/unit/test_core_cli.py`
| FR3 | Audio Capture | `src/kairos/audio/recorder.py:AudioRecorder` | `tests/integration/test_audio.py` (future)
| FR4 | Transcription | `src/kairos/asr/model.py:ASRModel.predict` | `tests/integration/test_asr.py` (future)
| FR5 | Intent Recognition | `src/kairos/nlp/intent.py:IntentProcessor` | `tests/unit/test_intent_processor.py`
| FR6 | Next/Previous Slide | `src/kairos/presentation/controller.py:next_slide/previous_slide` | `tests/unit/test_presentation_controller.py`
| FR7 | Jump to Slide | `src/kairos/presentation/controller.py:set_slide` | `tests/unit/test_presentation_controller.py`
| FR8 | Start/Stop Presentation | `src/kairos/presentation/controller.py:start_presentation/stop_presentation` | `tests/unit/test_presentation_controller.py`
| FR9 | List Presentations | `src/kairos/presentation/controller.py:get_presentations` | `tests/unit/test_presentation_controller.py`
| FR10 | Current Slide | `src/kairos/presentation/controller.py:get_current_slide` | `tests/unit/test_presentation_controller.py`
| FR11 | Error Handling | Logging and error returns in controller/HTTP client/audio | `tests/unit/test_http_presentation_client.py`
| FR12 | Configuration | `src/kairos/config.py`, `configs/default.yaml`, CLI `--config` | `tests/unit/test_core_cli.py`


