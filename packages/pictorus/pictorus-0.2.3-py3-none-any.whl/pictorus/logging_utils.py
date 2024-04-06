""" Logger utilities """
import logging

logging.basicConfig(format="%(asctime)s %(message)s")


def get_logger():
    """Get logger with common formatting"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger
