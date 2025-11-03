import os
import yaml


DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "configs", "default.yaml")


def _read_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(path: str | None = None) -> dict:
    """Load configuration from default and optional override path or env.

    Resolution order (last wins):
    - default.yaml (if present)
    - file provided by `path`
    - file provided by env var `KAIROS_CONFIG`
    """
    config = {}
    default_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "configs", "default.yaml"))
    if os.path.exists(default_path):
        config.update(_read_yaml(default_path))

    paths = []
    if path:
        paths.append(path)
    env_path = os.getenv("KAIROS_CONFIG")
    if env_path:
        paths.append(env_path)

    for p in paths:
        if os.path.exists(p):
            config.update(_read_yaml(p))

    return config

