import logging

# Configure basic settings for the logging system.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_logger(name):
    """
    Returns a logger instance with the specified name.
    """
    return logging.getLogger(name)