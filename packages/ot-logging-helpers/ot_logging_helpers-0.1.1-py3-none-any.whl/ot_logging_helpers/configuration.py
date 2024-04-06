import logging
import logging.config
from .custom_formatter import CustomFormatter

def configure_logging(format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level: str = "INFO"):

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "custom": {
                "()": CustomFormatter,
                "format": format
            }
        },
        "handlers": {
            "console": {
                "formatter": "custom",
                "class": "logging.StreamHandler",
            }
        },
        "loggers": {
            "": {"handlers": ["console"], "level": level},
        },
    })