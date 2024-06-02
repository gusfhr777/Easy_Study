import sys
import os
import datetime
import time
import traceback
# import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from model import *

VERSION = 'v0.0.1a'
DATE = '2024-06-02(수)'
AUTHOR = '한국항공대학교 컴퓨터공학과 24학번'
'''
현재 구현된 기능 목록(v0.0.1a)
- 강의 목록 크롤링
- 개별 강의 활동 목록 크롤링
- 시청하지 않은 영상 자동시청
- 자동로그인 지원
- 멋진 CLI 및 프로그램 크레딧

구현해야 하는 기능(v0.0.1a)

추후 구현할 기능
- 업데이트 예고
- 과제 남은기간 알림 기능
- 스케줄러 활용한 프로그램 자동실행(특정 시간마다 확인 및 자동실행)
- 파일 및 동영상 일괄 다운로드

이후 할 일
- 타 LMS 지원을 위한 프로그램 일반화
- 알고리즘 최적화
- 안정성 확보(traceback)
- 로거 구현
- 보안 강화
- 프로그램 배포
- 오픈소스화
- 컴파일 방법 배포
- 이후의 LMS 기능변화 대응
'''
KAU = ''''''

class DriverController: #드라이버 제어 클래스.
    def __init__(self):
        self.isLogin = False
        self.isAutoLogin = True # 자동로그인 여부. 2차 이후 가능.
        self.isHandleLess = False #2차 이후 가능. not headless for this version v0.0.1a
        self.isWatchAll = True # Check All Video for this version v0.0.1a

        try:
            with open('autoVideo.txt', 'r'):
                self.isAutoVideo = True
        except:
            self.isAutoVideo = False
            
        self.__driverInit()


    def systemUpdateCheck(self): # 돈이 없어요.. 업뎃서버 살 돈을 주세요
        pass

    def __driverInit(self): #드라이버 초기화 함수
        print('로딩중... 시간이 조금 걸려요')
        try:
            service = Service(excutable_path=ChromeDriverManager().install())
        except:
            traceback.format_exc()
            print('오류 발견됨. 인터넷 연결이 되어있는지 확인하세요.')
        options = uc.ChromeOptions()
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-application-cache')
        options.add_argument('--disable-gpu')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--user-data-dir=c:\ChromeMetaData")
        options.set_capability('unhandledPromptBehavior', 'ignore')

        try:
            if __debug__:
                self.driver = uc.Chrome(options=options, service=service)
                self.driver.implicitly_wait(15)
            else:
                self.driver = webdriver.Chrome(service=service)
        except Exception:
            traceback.format_exc()
            print('크롬 실행에 실패하였습니다. 자세한 사항은 프로그램 설명서를 참고하시고, 그래도 발생 시, 개발자에게 문의바랍니다.')
            input('엔터키를 눌러 종료합니다.')

        print('로딩 성공! 히히')

    def login(self): #LMS 로그인 함수
        print('LMS 사이트에서 로그인하시기 바랍니다.')
        login_url = 'https://lms.kau.ac.kr/login.php'
        self.driver.get(login_url)
        while True:
            time.sleep(1)
            if self.isAutoLogin:
                self.driver.find_element(By.CLASS_NAME, 'btn-success').click()
                try:
                    alert = self.driver.switch_to.alert
                    alert.accept()
                    print('자동로그인 실패. 로그인 바랍니다.')
                    self.isAutoLogin = False
                except:
                    pass

            if self.driver.current_url == 'https://lms.kau.ac.kr/':
                break
            else:
                continue
        self.islogin = True
        print('로그인 성공. 자동로그인을 원하는 경우, 비밀번호 저장 버튼을 눌러주세요.')


    def crawlCourseList(self): # 수강목록 리스트 크롤링 함수
        Course.course_list = []
        Course.unwatched_video_list = []

        lms_website = 'https://lms.kau.ac.kr/'
        self.driver.get(lms_website)
        # self.driver.implicitly_wait(5)
        time.sleep(1)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        crawled_course_list = soup.find('div', {'class':'course_lists'}).findAll('li')
        for i in crawled_course_list:
            link = i.find('a').attrs['href']

            course_title_div = i.find('div',{'class':'course-title'})
            title_element = course_title_div.find('h3')
            if title_element.find('span'):
                title_element.find('span').decompose()

            course_label_div = i.find('div', {'class':'course-label'})

            title = title_element.text
            professor = course_title_div.find('p', {'class':'prof'}).text
            course_label = course_label_div.find('div',{'class':'label'}).text
            course_label_under = course_label_div.find('div',{'class':'label-under'}).text

            Course(title, professor, link, course_label, course_label_under)
            print(title)
        Course.save()
        print('강의목록 탐색이 완료되었습니다.')

    def __activity_list_process(self, activity_list_div): # 강의 내 Activity 리스트 처리 함수
        activity_list = []

        for activity_div in activity_list_div:
            #preprocess for title
            activity_div.find('span', {'class':'instancename'})
            instancename = activity_div.find('span', {'class':'instancename'}) # 제목 span. 내부 span에 activity type이 적혀있는 경우가 있어서 제거한다.
            if instancename == None: #아무 링크 없는 일반 텍스트.
                continue
            if instancename.find('span', {'accesshide'}) == None: #아무 링크 없는 일반 텍스트.
                continue
            if activity_div.find('div', {'class':'dimmed_text'}): #outdated file. pass for this version 0.0.1a
                continue
            instancename.find('span', {'accesshide'}).decompose()
            activity_title = instancename.text

            display_option = activity_div.find('span', {'class': 'displayoptions'})
            if display_option:
                text_ubstrap = display_option.find('span', {'class': 'text-ubstrap'}) #기간제한 텍스트
                if text_ubstrap:
                    activity_datefrom, activity_dateto = map(str.strip, text_ubstrap.text.strip().split('~'))
                else:
                    activity_datefrom, activity_dateto = '기간 제한 없음', '기간 제한 없음'
            else: #activity type URL. pass for this version 0.0.1a
                continue
            activity_link = activity_div.find('div', {'class':'activityinstance'}).find('a').attrs['href']

            if 'ubfile' in activity_div.attrs['class']: #ubfile
                text_info = activity_div.find('span', {'class': 'displayoptions'}).find('span', {'class': 'text-info'}).text.strip()

                s = text_info.split()
                if ('바이트' or 'Byte') in text_info:
                    activity_file_size = s[0] + 'Bytes'
                    text_info = ' '.join(s[2:]).strip()
                else:
                    activity_file_size = s[0]
                    text_info = ' '.join(s[1:]).strip()

                if 'PDF' in text_info:
                    activity_file_type = 'pdf'
                elif 'ZIP' in text_info:
                    activity_file_type = 'zip'
                elif ('워드 문서' or 'word' or 'WORD') in text_info:
                    activity_file_type = 'docx'
                elif ('한글 문서' or 'hwp' or 'HWP') in text_info:
                    activity_file_type = 'hwp'
                else:
                    activity_file_type = text_info

                activity = FileActivity(activity_title, activity_link, activity_datefrom, activity_dateto, activity_file_size, activity_file_type)

            elif 'vod' in activity_div.attrs['class']: #vod
                print(f'{activity_title} 동영상 발견')
                time_list = list(map(int,activity_div.find('span', {'class':'displayoptions'}).find('span',{'class':'text-info'}).text.replace(',','').strip().split(':')))
                if len(time_list) == 2:
                    hour = 0
                    min = time_list[0]
                    sec = time_list[1]
                elif len(time_list) == 3:
                    hour = time_list[0]
                    min = time_list[1]
                    sec = time_list[2]
                activity_video_length = hour*3600+min*60+sec
                activity = VideoActivity(activity_title, activity_link, activity_datefrom, activity_dateto, activity_video_length)
            elif 'quiz' in activity_div.attrs['class']: #quiz
                activity = Activity(activity_title, activity_link, activity_datefrom, activity_dateto)
            elif 'choice' in activity_div.attrs['class']: #choice
                activity = Activity(activity_title, activity_link, activity_datefrom, activity_dateto)
            elif 'assign' in activity_div.attrs['class']:
                activity = Activity(activity_title, activity_link, activity_datefrom, activity_dateto)
            else: #else
                activity = Activity(activity_title, activity_link, activity_datefrom, activity_dateto)
            activity_list.append(activity)
        return activity_list

    def __week_process(self, week_div, course): #강의 내 Week 처리 함수
        week_title = week_div.find('span', {'class': 'sectionname'}).text
        week_summary = week_div.find('div', {'class': 'summary'}).text
        week_week = len(course.week_list) + 1
        week = WeekSection(week_title, week_summary, week_week)
        print(week_title)
        activity_list_ul = week_div.find('ul', {'class': 'section img-text'})
        if activity_list_ul == None:
            return
        else:
            course.week_list.append(week)
            activity_list_div = activity_list_ul.findAll('li', {'class': 'activity'})
            week.activity_list.extend(self.__activity_list_process(activity_list_div))

    def crawlCourse(self): #강의 크롤링 함수.
        print('강의 탐색을 시작합니다.')
        for course in Course.course_list:
            print(f'{course.title} 강의 {course.professor} 교수 탐색중')
            self.driver.get(course.link)
            time.sleep(1.5)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            total_sections = soup.find('div', {'class': 'total_sections'})
            if 'topics' in total_sections.find('ul').attrs['class']:
                week_div = soup.find('div', {'class': 'total_sections'}).find('ul', {'class': 'topics ubstopics'}).find('li')
                self.__week_process(week_div, course)
            else:
                week_list_div = soup.find('div', {'class': 'total_sections'}).find('ul', {'class': 'weeks ubsweeks'}).findAll('li', {
                'class': 'section'})
                for week_div in week_list_div:
                    self.__week_process(week_div, course)
            print()

        Course.save()
        print('강의 탐색이 완료되었습니다.')

    def crawlUnWatched(self): # 안 본 동영상 크롤링 함수
        video_list = Course.getAllActivityList(VideoActivity)
        print(f'총 확인된 영상 개수 : {len(video_list)}개')

        if self.isWatchAll:
            for course in Course.course_list: # find all video for this version v0.0.1a
                print(course.title)
                for video in course.getActivityList(VideoActivity):
                    print('동영상 ', video.title)
                    self.driver.get(video.link)
                    wait = WebDriverWait(self.driver, 10)
                    second_button = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'동영상 보기')]")))
                    second_button.click()
                    video_window = self.driver.window_handles[1]
                    self.driver.switch_to.window(video_window)
                    time.sleep(0.5)
                    try:
                        alert = self.driver.switch_to.alert
                        alert.dismiss()
                    except:
                        pass
                    main_window = self.driver.window_handles[0]
                    # time.sleep(10)
                    # script = f"window.open('{video.link}', 'VodContentWindow','toolbar=0,scrollbars=0,location=0,menubar=0,status=0,width=1005,height=755');return false;"
                    # self.driver.execute_script(script)

                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    close_message = soup.find('div', {'class': 'window_close_message'})

                    if close_message:
                        video.isWatched = False
                        print(f'{video.title} 미시청 확인됨')
                        Course.unwatched_video_list.append(video)

                    # print('after', self.driver.window_handles)
                    self.driver.close()
                    self.driver.switch_to.window(main_window)

        Course.save()
        print('동영상 시청 여부 확인이 완료되었습니다.\n')


    def watchUnwatchedVideo(self): #보지 않은 영상 시청 함수
        print('영상 시청을 시작합니다.')
        for video in Course.unwatched_video_list:
            video_timedelta = datetime.timedelta(seconds=video.video_length)
            if video_timedelta.seconds//3600 > 0:
                hours, minutes, seconds = video.video_length//3600, (video.video_length%3600)//60, video.video_length%60
                t = f'{hours}:{minutes}:{seconds}'
            else:
                minutes, seconds = (video.video_length % 3600) // 60, video.video_length % 60
                t = f'{minutes}:{seconds}'
            eta = (datetime.datetime.now() + video_timedelta).strftime('%Y-%m-%d %H:%M:%S')

            print(f'{t} {video.title} 완료시각 {eta}', end='')

            self.driver.get(video.link)
            wait = WebDriverWait(self.driver, 10)
            second_button = wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'동영상 보기')]")))
            second_button.click()
            video_window = self.driver.window_handles[1]
            self.driver.switch_to.window(video_window)
            time.sleep(0.5)
            try:
                alert = self.driver.switch_to.alert
                alert.dismiss()
            except:
                pass
            main_window = self.driver.window_handles[0]

            self.driver.find_element(By.XPATH, '//*[@id="vod_player"]/div[2]/video').click()
            time.sleep(video.video_length)
            video.isWatched = True
            self.driver.close()

            self.driver.switch_to.window(main_window)
        Course.unwatched_video_list = []
        Course.save()
        print('모든 영상을 시청완료하였습니다. 수고하셨습니다.')


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
            print(i)
            time.sleep(0.02)
        print(f'''    LMS 자동시청 및 기능편의 프로그램 | 편한수강 {VERSION}
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
        command = input('명령어 입력 : ')
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
            print('프로그램 종료중.. 잠시만 기다려주세요')
            dc.driver.quit()
            exit()
        else:
            pass

if __name__ == "__main__":
    main()