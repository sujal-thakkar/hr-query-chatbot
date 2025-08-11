import logging
import logging
import os
import sys
from typing import Optional

def setup_logging(level: Optional[str] = None) -> None:
    """Initialize basic structured logging for the backend.

    Env: LOG_LEVEL (default INFO)
    """
    log_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Root logger config
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Reduce noise from third-party libraries if needed
    for noisy in ("httpx", "urllib3"):
        logging.getLogger(noisy).setLevel(max(logging.WARNING, numeric_level))

    logging.getLogger(__name__).info("Logging initialized at %s", log_level)
