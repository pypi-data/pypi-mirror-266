# src/bump440/logger.py

import logging


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set the logging level
    handler = logging.StreamHandler()  # Create a handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )  # Create a formatter
    handler.setFormatter(formatter)  # Set the formatter for the handler
    logger.addHandler(handler)  # Add the handler to the logger
    return logger
