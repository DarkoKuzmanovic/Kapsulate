import logging
import os
import sys

def setup_logging(base_dir):
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "kapsulate.log")

    logger = logging.getLogger("kapsulate")
    logger.setLevel(logging.DEBUG)

    # Console handler
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setLevel(logging.INFO)

    # File handler
    f_handler = logging.FileHandler(log_file)
    f_handler.setLevel(logging.DEBUG)

    # Create formatters and add it to handlers
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    c_format = logging.Formatter(format_str)
    f_format = logging.Formatter(format_str)
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger

def get_logger():
    return logging.getLogger("kapsulate")
