import logging
import traceback
import os
from model import log_queue

LOGGER_PATH = 'logs/es.log'
LOGGER_NAME = 'es_logger'

def __loggerInit():
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] : %(message)s')

    try:
        file_handler = logging.FileHandler(LOGGER_PATH)
    except:
        os.mkdir('./logs')
        with open(LOGGER_PATH, 'w', encoding='utf-8') as f:
            pass
        file_handler = logging.FileHandler(LOGGER_PATH)
    
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

logger = __loggerInit()

def log_print(txt):
    logger.info(txt)
    log_queue.append(txt)

def report(reason='', driver=None):
    if driver:
        with open('report.html') as f:
            f.write(driver.page_source)

    if reason:
        log_queue.append(reason)

    logger.critical(traceback.format_exc())