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

def log_print(txt='', end='\n'):
    logger.info(txt)
    log_queue.put(txt+end)

def report(reason='프로그램 실행 중 오류가 발생하였습니다. logs폴더와 함께 개발자에게 문의하세요. 이메일 gkrgus777@kau.kr', driver=None):
    logger.critical(traceback.format_exc())
    if reason:
        log_queue.put('\n\n버그 발생\n'+reason)

    if driver:
        with open('logs/report.html', 'w', encoding='utf-8') as f:
            try:
                f.write(driver.page_source)
            except:
                log_queue.put('소스코드 출력 실패')
            # print('driver printed.')
            # print(driver.page_source)
