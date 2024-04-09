"""Module describing a Logger."""

import sys
import logging
import logging.handlers

LOGGER_FORMATTER = "%(asctime)s %(levelname)-8s: %(message)s", "%Y-%m-%d %H:%M:%S"
# RANCH_LOGREPORT = ""


class Logger(logging.Logger):
    """
    Logger creates a new logger, outputing to a file (FileHandler).
    """

    # MAX_LOG_SIZE = 5 * 1024 * 1024  # Size threshold before rotation
    # BACKUP_COUNT = 3  # Number of log rotate

    def __init__(self):
        super().__init__("ranchecker")

        # self.file_handler = logging.handlers.RotatingFileHandler(
        #     RANCH_LOGREPORT, maxBytes=self.MAX_LOG_SIZE, backupCount=self.BACKUP_COUNT
        # )

        self.file_handler = logging.StreamHandler(sys.stdout)

        self.file_handler.setFormatter(logging.Formatter(LOGGER_FORMATTER))
        self.file_handler.setLevel(logging.DEBUG)  # log everything in file
        self.addHandler(self.file_handler)

    def close_file(self):
        self.file_handler.close()

    # methods below for a context management (with Logger(...) as logger:)
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_file()
