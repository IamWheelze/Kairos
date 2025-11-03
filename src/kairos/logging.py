import logging
import os


_CONFIGURED = False


def _ensure_configured():
    global _CONFIGURED
    if _CONFIGURED:
        return
    level_name = os.getenv("KAIROS_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    _CONFIGURED = True


def get_logger(name: str):
    _ensure_configured()
    return logging.getLogger(name)

