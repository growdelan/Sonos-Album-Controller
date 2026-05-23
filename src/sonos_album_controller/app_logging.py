import logging
from pathlib import Path


def get_app_logger(log_path: Path) -> logging.Logger:
    logger = logging.getLogger("sonos_album_controller")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    target = str(log_path)
    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler) and handler.baseFilename == target:
            return logger
        logger.removeHandler(handler)
        handler.close()

    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger
