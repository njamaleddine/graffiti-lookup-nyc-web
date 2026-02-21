import logging

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO


def get_logger(name=None, level=LOG_LEVEL, format=LOG_FORMAT):
    logging.basicConfig(level=level, format=format)
    return logging.getLogger(name)
