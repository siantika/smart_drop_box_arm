'''
    It is functional program

'''

import logging

LOG_DIR = "./log/logger_device.txt"

# Create a logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a console handler and set its log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create a file handler and set its log level
fh = logging.FileHandler(LOG_DIR)
fh.setLevel(logging.DEBUG)

# Create a formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(ch)
logger.addHandler(fh)

