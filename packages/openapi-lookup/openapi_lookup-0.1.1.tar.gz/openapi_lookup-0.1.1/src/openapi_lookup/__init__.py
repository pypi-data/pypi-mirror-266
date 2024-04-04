"""Open API Lookup package."""

import logging
import os
from pathlib import Path


app_name = "openapi_lookup"
app_root = Path(__file__).parent.parent.absolute()
logs_dir = os.path.join(app_root, "var", "logs")
verbosity_levels = [
    logging.ERROR,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG,
]
log_level = verbosity_levels[0]


def setup_logger() -> logging.Logger:
    """Setup logger."""
    # Create logger
    logger = logging.getLogger(__name__)

    # Set log level
    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    # Create console handler and set level and formatter
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)

    # Add console handler to logger
    logger.addHandler(ch)

    # Create file handler and set level and formatter
    log_file_path = os.path.join(logs_dir, f"{app_name}.log")
    if os.path.exists(logs_dir) is False:
        os.makedirs(logs_dir)

    fh = logging.FileHandler(log_file_path)
    fh.setLevel(log_level)
    fh.setFormatter(formatter)

    # Add file handler to logger
    logger.addHandler(fh)

    return logger
