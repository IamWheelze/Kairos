from loguru import logger

logger.add(
    "backend/logs/kairos.log",
    rotation="5 MB",
    retention=5,
    enqueue=True,
    backtrace=True,
    diagnose=False,
)

__all__ = ["logger"]

