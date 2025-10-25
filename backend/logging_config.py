#!/usr/bin/env python3

"""

"""

from dotenv import load_dotenv
from typing import Any
import logging.config
import os

load_dotenv()

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": ("[PharmacyApp] - %(asctime)s - %(levelname)s - %(name)s -"
            " lineno. %(lineno)d - %(message)s")
        }
    },
    "handlers": {
        "models_files": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "interval": 1,
            "backupCount": 1,
            "filename": "logs/models.log",
            "formatter": "standard",
        },
        "api_files": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "interval": 1,
            "backupCount": 1,
            "filename": "logs/api.log",
            "formatter": "standard",
        },
        "test_files": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "interval": 1,
            "backupCount": 1,
            "filename": "logs/tests.log",
            "formatter": "standard",
        },
    },
    "loggers": {
        "models": {
            "handlers": ["models_files"],
            "level": "DEBUG",
        },
        "api": {
            "handlers": ["api_files"],
            "level": "DEBUG",
        },
        "__main__": {
            "handlers": ["api_files"],
            "level": "DEBUG",
        },
        "tests": {
            "handlers": ["test_files"],
            "level": "DEBUG",
        }
    }
}

def setup_logging() -> None:
    """Setup logging configurations"""
    os.makedirs("logs", exist_ok=True)

    debug_mode = os.getenv("DEBUG_MODE", "False")
    if not debug_mode:
        raise ValueError("No environment variable for debug mode.")
    
    log_level = "DEBUG" if debug_mode == "True" else "WARNING"
    for logger in LOGGING_CONFIG["loggers"].values():
        logger["level"] = log_level
    logging.config.dictConfig(LOGGING_CONFIG)
