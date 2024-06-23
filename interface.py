from driverController import DriverController
import sys
import os
import time
from loggingInterface import log_print, report
from model import *

VERSION = 'v0.2.0a'
DATE = '2024-06-23(일)'
AUTHOR = '한국항공대학교 컴퓨터공학과'
'''
현재 구현된 기능 목록(v0.2.0a)
- 로거 구현
- 입장하지 않은 강의에서 멈추는 오류 수정

구현해야 하는 기능(v0.2.0a)
- 특정 과목만 선택

추후 구현할 기능
- 업데이트 예고
- 과제 남은기간 알림 기능
- 스케줄러 활용한 프로그램 자동실행(특정 시간마다 확인 및 자동실행)
- 파일 및 동영상 일괄 다운로드 # no

이후 할 일
- 타 LMS 지원을 위한 프로그램 일반화
- 알고리즘 최적화
- 안정성 확보(traceback)
- 보안 강화
- 프로그램 배포
- 오픈소스화
- 컴파일 방법 배포
- 이후의 LMS 기능변화 대응
'''
KAU = ''''''

def watch(dc):
    dc.login()
    dc.crawlCourseList()
    dc.crawlCourse()
    dc.crawlUnWatched()
    dc.watchUnwatchedVideo()

def main():
    dc = DriverController()
    Course.load()
    if not Course.course_list:
        isFirst = True
    else:
        isFirst = False
    
    if dc.isAutoVideo:
        watch(dc)
        input('아무 키를 눌러 종료합니다.')
        dc.driver.quit()
        exit()


    while True:
        if sys.platform == 'win32':
            os.system('cls')
        else:
            os.system('clear')
        for i in KAU.split('\n'):
            log_print(i)
            time.sleep(0.02)
        log_print(f'''    LMS 자동시청 및 기능편의 프로그램 | 편한수강 {VERSION}
    배포일 : {DATE}
    제작자 : {AUTHOR}
    본 프로그램은 항공대 LMS 전용으로, 타 LMS에서의 작동을 보장하지 않습니다.
    본 프로그램은 항공대 공식 프로그램이 아닙니다.
    
    현재 상태
    LMS 자동로그인 여부 : {'O' if dc.isAutoLogin else 'X'}
    {'프로그램을 처음 실행한 상태입니다.' if isFirst else ''}
    
    명령어 목록
    1 : LMS 미시청 영상 자동시청
    2 : 자동로그인 ON/OFF
    3 : 강의 관련 데이터 출력
    4 : 자동시청 Flag 생성
    5 : 과제/퀴즈 남은기간 자동알림 ON/OFF - 미구현
    6 : 특정 시간마다 자동 확인 및 시청 ON/OFF - 미구현
    7 : 파일 일괄 다운로드 - 미구현
    8 : 동영상 일괄 다운로드 - 미구현
    9 : 공지사항 타임라인별 출력 - 미구현
    
    0 : 프로그램 종료
    ''')
        command = input('명령어(숫자) 입력 : ')
        if command == "1":
            watch(dc)
            input('계속하려면 아무 키를 누르세요.')
        elif command == '2':
            dc.isAutoLogin = not dc.isAutoLogin
        elif command == '3':
            Course.printCourse()
            input('엔터키를 눌러 메인창으로 넘어갑니다.')
        elif command == '4':
            with open('autoVideo.txt', 'w') :pass
        if command in ('q', 'quit', 'QUIT', 'Q', '종료', '0'):
            log_print('프로그램 종료중.. 잠시만 기다려주세요')
            dc.driver.quit()
            exit()
        else:
            pass
