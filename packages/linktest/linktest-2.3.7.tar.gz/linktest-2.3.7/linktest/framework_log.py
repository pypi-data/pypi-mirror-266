"""
This module is used to:
 create the framework_logger instance

@author: Wang Lin
"""
import logging
import importlib
import os
import sys
from . import get_project_info

execution_log_file = get_project_info.get_project_info().project_path + os.sep + "output" + os.sep + get_project_info.ProjectInfo.start_time_for_output + os.sep + "execution.log"

# importlib.reload(logging)

# Log file location
logfile = execution_log_file

# Define the log format
log_format = ('%(asctime)s [%(threadName)-12.12s] %(levelname)s %(filename)s %(lineno)d: %(message)s')

# Define basic configuration
logging.basicConfig(
    # Define logging level
    level=logging.DEBUG,
    # Declare the object we created to format the log messages
    format=log_format,
    # Declare handlers
    handlers=[
        logging.FileHandler(logfile),
        logging.StreamHandler(sys.stdout),
    ]
)

framework_logger = logging

framework_logger.info("framework_logger created ...")
