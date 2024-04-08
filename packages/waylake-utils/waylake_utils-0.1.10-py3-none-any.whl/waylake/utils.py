import logging.handlers
import os
from typing import Dict, Any

import yaml


def setup_logger(name: str, caller_file: str, log_dir: str = "logs", logger_config: dict = None) -> logging.Logger:
    """
    Set up a logger with file and console handlers in the specified directory.

    :param name: Name for the logger.
    :param caller_file: File path of the calling script to determine log directory.
    :param log_dir: Directory for log files, defaults to 'logs'.
    :param logger_config: Optional dictionary containing logger configuration. If provided, this configuration will be used.
    :return: Configured logger object.
    """
    # Determine the absolute path to the log directory based on the caller's file location
    base_path = os.path.dirname(os.path.abspath(caller_file))
    log_path = os.path.join(base_path, log_dir)

    # Create the log directory if it doesn't exist
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # Configure logging
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        "[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s"
    )

    # File handler
    fileHandler = logging.FileHandler(os.path.join(log_path, f"{name}.log"))
    fileHandler.setFormatter(formatter)

    # Stream handler (for console output)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    # If logger_config is provided, update logger configuration
    if logger_config:
        for key, value in logger_config.items():
            if hasattr(logger, key):
                setattr(logger, key, value)

    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)
    logger.setLevel(logging.DEBUG)

    return logger


def load_cofnig(config_file: str) -> Dict[str, Any]:
    """
    Load a YAML configuration file.

    :param config_file: Path to the configuration file.
    :return: Dictionary of configuration values.
    """
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    return config
