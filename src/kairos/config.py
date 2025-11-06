"""Configuration loading and management for Kairos.

This module handles loading configuration from YAML files with support for
defaults and overrides via file paths or environment variables.
"""

import os
import yaml
from kairos.logging import get_logger

log = get_logger("kairos.config")

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "configs", "default.yaml")


def _read_yaml(path: str) -> dict:
    """Read and parse a YAML configuration file.

    Args:
        path: Path to the YAML file

    Returns:
        Dictionary of configuration values or empty dict on error
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            if config is None:
                log.warning("Empty configuration file: %s", path)
                return {}
            if not isinstance(config, dict):
                log.error("Configuration file is not a dict: %s", path)
                return {}
            log.debug("Loaded configuration from: %s", path)
            return config
    except FileNotFoundError:
        log.error("Configuration file not found: %s", path)
        return {}
    except yaml.YAMLError as e:
        log.error("YAML parsing error in %s: %s", path, e)
        return {}
    except Exception as e:
        log.error("Error reading configuration %s: %s", path, e)
        return {}


def load_config(path: str | None = None) -> dict:
    """Load configuration from default and optional override path or env.

    Resolution order (last wins):
    - default.yaml (if present)
    - file provided by `path`
    - file provided by env var `KAIROS_CONFIG`

    Args:
        path: Optional path to configuration file

    Returns:
        Dictionary of merged configuration values
    """
    config = {}

    # Load default configuration
    default_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "configs", "default.yaml")
    )
    if os.path.exists(default_path):
        default_config = _read_yaml(default_path)
        if default_config:
            config.update(default_config)
            log.info("Loaded default configuration from: %s", default_path)
    else:
        log.warning("Default configuration not found at: %s", default_path)

    # Collect override paths
    override_paths = []
    if path:
        override_paths.append(path)
    env_path = os.getenv("KAIROS_CONFIG")
    if env_path:
        override_paths.append(env_path)
        log.debug("Configuration override from KAIROS_CONFIG: %s", env_path)

    # Load and merge overrides
    for p in override_paths:
        if not os.path.exists(p):
            log.warning("Configuration file not found: %s", p)
            continue

        override_config = _read_yaml(p)
        if override_config:
            config.update(override_config)
            log.info("Loaded configuration override from: %s", p)

    if not config:
        log.warning("No configuration loaded, using empty config")

    return config


def validate_config(config: dict) -> bool:
    """Validate configuration has required fields.

    Args:
        config: Configuration dictionary to validate

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(config, dict):
        log.error("Configuration is not a dictionary")
        return False

    # Check for expected top-level keys (optional, for future validation)
    expected_sections = ["audio", "asr", "nlp", "presentation"]
    found_sections = [s for s in expected_sections if s in config]

    if found_sections:
        log.debug("Configuration sections found: %s", found_sections)
    else:
        log.warning("No standard configuration sections found")

    return True

