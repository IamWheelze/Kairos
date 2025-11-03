import os
from kairos.core import Kairos


def test_core_lifecycle_start_stop_status(tmp_path):
    # Use default config implicitly
    k = Kairos()
    assert k.get_status() == "stopped"

    k.start()
    assert k.get_status() == "running"

    k.stop()
    assert k.get_status() == "stopped"


def test_core_config_loading(monkeypatch, tmp_path):
    # Create a custom config file overriding audio filename
    cfg = tmp_path / "custom.yaml"
    cfg.write_text("""
audio:
  filename: test_output.wav
asr:
  model_name: tiny
""".strip())

    k = Kairos()
    k.start(config_path=str(cfg))
    # Verify config applied
    assert k.config.get("asr", {}).get("model_name") == "tiny"
    assert getattr(k.audio_recorder, "filename", None) == "test_output.wav"

