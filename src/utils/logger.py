# manual: https://betterstack.com/community/guides/logging/logging-with-fastapi/
LOG_FOLDER = "logs"

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file_backend": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": f"{LOG_FOLDER}/fastapi.log",
            "mode": "a",
        },
        "file_frontend": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": f"{LOG_FOLDER}/frontend.log",
            "mode": "a",
        },
    },
    "loggers": {
        "app": {
            "handlers": ["console", "file_backend"],
            "level": "DEBUG",
            "propagate": True,
        },
        "frontend": {
            "handlers": ["file_frontend"],
            "level": "DEBUG",
        },
    },
    # "root": {"handlers": ["console"], "level": "DEBUG"},
}
