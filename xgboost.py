#!/usr/bin/env python

from __future__ import print_function  # For compatibility with Python 2 and 3
import subprocess
import sys
import locale
import logging
from logging.handlers import RotatingFileHandler

# Determine the system's default encoding
default_encoding = locale.getpreferredencoding()

# Configure logging
log_file = '/var/tmp/DMZ.log'
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
log_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=1)
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

def log_and_exit(message, exit_code=1):
    logger.error(message)
    sys.exit(exit_code)
