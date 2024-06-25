
import datetime
import time
import threading
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import m3u8_To_MP4


from loggingInterface import log_print, report
from model import *

class DriverController: #드라이버 제어 클래스.
    def __init__(self):
        threading.Thread(target=self.__initThread).start()
    
    def __initThread(self):
        try:
            self.isLogin = False
            self.isAutoLogin = True # 자동로그인 여부. 2차 이후 가능.
            self.isHandleLess = False #2차 이후 가능. not headless for this version v0.0.1a
            self.isWatchAll = True # Check All Video for this version v0.0.1a

            try:
                with open('autoVideo.txt', 'r'):
                    self.isAutoVideo = True
            except:
                self.isAutoVideo = False
                
            log_print('크롬 로딩중... 시간이 조금 걸려요')
            self.__driverInit()
            self.login()
        except:
            report(driver=self.driver)


    def __driverInit(self): #드라이버 초기화 함수
        self.driver = None
        try:
            service = Service(excutable_path=ChromeDriverManager().install())
        except:
            report('오류 발견됨. 인터넷 연결이 되어있는지 확인하세요.')
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
        except:
            report('크롬 실행에 실패하였습니다. 자세한 사항은 프로그램 설명서를 참고하시고, 그래도 발생 시, 개발자에게 문의바랍니다.')
            

        log_print('로딩 성공!')

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
                log_print(f'{activity_title} 동영상 발견')
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
        if week_div == None:
            return
        week_title = week_div.find('span', {'class': 'sectionname'}).text
        week_summary = week_div.find('div', {'class': 'summary'}).text
        week_week = len(course.week_list) + 1
        week = WeekSection(week_title, week_summary, week_week)
        log_print(week_title)
        activity_list_ul = week_div.find('ul', {'class': 'section img-text'})
        if activity_list_ul == None:
            return
        else:
            course.week_list.append(week)
            activity_list_div = activity_list_ul.findAll('li', {'class': 'activity'})
            week.activity_list.extend(self.__activity_list_process(activity_list_div))

    def login(self): #LMS 로그인 함수
        log_print('LMS 사이트에서 로그인하시기 바랍니다.')
        login_url = 'https://lms.kau.ac.kr/login.php'
        self.driver.get(login_url)
        while True:
            time.sleep(1)
            if self.isAutoLogin:
                self.driver.find_element(By.CLASS_NAME, 'btn-success').click()
                try:
                    alert = self.driver.switch_to.alert
                    alert.accept()
                    log_print('자동로그인 실패. 로그인 바랍니다.')
                    self.isAutoLogin = False
                except:
                    pass

            if self.driver.current_url == 'https://lms.kau.ac.kr/':
                break
            else:
                continue
        self.isLogin = True
        log_print('로그인 성공. 자동로그인을 원하는 경우, 비밀번호 저장 버튼을 눌러주세요.')

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
            log_print(title)
        Course.save()
        log_print('강의목록 탐색이 완료되었습니다.')

    def crawlCourse(self): #강의 크롤링 함수.
        log_print('강의 탐색을 시작합니다.')
        for course in Course.course_list:
            log_print(f'{course.title} 강의 {course.professor} 교수 탐색중')
            self.driver.get(course.link)
            time.sleep(1.5)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            if soup.find('div',{'class':'error_message'}):#아직 교수자가 가상 강의실에 입장하지 않아 학생들에게 나타나지 않는 강좌입니다. 향후 교수자가 본 강의실에 입장하시면 자동으로 이용하실 수 있습니다.
                continue

            total_sections = soup.find('div', {'class': 'total_sections'})
            if 'topics' in total_sections.find('ul').attrs['class']:
                week_div = soup.find('div', {'class': 'total_sections'}).find('ul', {'class': 'topics ubstopics'}).find('li')
                self.__week_process(week_div, course)
            else:
                week_list_div = soup.find('div', {'class': 'total_sections'}).find('ul', {'class': 'weeks ubsweeks'}).findAll('li', {
                'class': 'section'})
                for week_div in week_list_div:
                    self.__week_process(week_div, course)
            log_print()

        Course.save()
        log_print('강의 탐색이 완료되었습니다.')

    def crawlUnWatched(self): # 안 본 동영상 크롤링 함수
        video_list = Course.getAllActivityList(VideoActivity)
        log_print(f'총 확인된 영상 개수 : {len(video_list)}개')

        if self.isWatchAll:
            for course in Course.course_list: # find all video for this version v0.0.1a
                log_print(course.title)
                for video in course.getActivityList(VideoActivity):
                    log_print('동영상 '+ video.title)
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


                    page = self.driver.page_source
                    location = page.find('https://fcbjngaswqol4996171.cdn.ntruss.com')
                    m3u8 = page[location:location+139]
                    video.m3u8 = m3u8
                    soup = BeautifulSoup(page, 'html.parser')
                    close_message = soup.find('div', {'class': 'window_close_message'})

                    if close_message:
                        video.isWatched = False
                        log_print(f'{video.title} 미시청 확인됨')
                        Course.unwatched_video_list.append(video)

                    # log_print('after', self.driver.window_handles)
                    self.driver.close()
                    self.driver.switch_to.window(main_window)

        Course.save()
        log_print('동영상 시청 여부 확인이 완료되었습니다.\n')

    def watchUnwatchedVideo(self, var_states): #보지 않은 영상 시청 함수
        log_print('영상 시청을 시작합니다.')
        for i, video in enumerate(Course.unwatched_video_list):
            var = var_states[i].get()
            if not var:
                continue
            video_timedelta = datetime.timedelta(seconds=video.video_length)
            if video_timedelta.seconds//3600 > 0:
                hours, minutes, seconds = video.video_length//3600, (video.video_length%3600)//60, video.video_length%60
                t = f'{hours}:{minutes}:{seconds}'
            else:
                minutes, seconds = (video.video_length % 3600) // 60, video.video_length % 60
                t = f'{minutes}:{seconds}'
            eta = (datetime.datetime.now() + video_timedelta).strftime('%Y-%m-%d %H:%M:%S')

            log_print(f'{t} {video.title} 완료시각 {eta}', end='')

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
            time.sleep(int(video.video_length*1.05))
            self.driver.find_element(By.CLASS_NAME, 'vod_close_button').click()
            self.driver.switch_to.alert.accept()
            video.isWatched = True

            self.driver.switch_to.window(main_window)
        Course.unwatched_video_list = []
        Course.save()
        log_print('모든 영상을 시청완료하였습니다')
    
    def downloadVideo(self, var_states):
        if not os.path.exists('./output/'):os.mkdir('./output/')
        log_print('\n동영상 다운로드를 시작합니다.')
        for i, video in enumerate(Course.getAllActivityList(VideoActivity)):
            if not var_states[i].get(): continue
            for course in Course.course_list:
                if video in course.getActivityList(VideoActivity):
                    subject_name = course.title
            file_dir = './output/' + subject_name + '/'
            if not os.path.exists(file_dir):os.mkdir(file_dir)
            log_print('다운로드 중 : '+video.title)
            m3u8_To_MP4.multithread_download(m3u8_uri=video.m3u8, mp4_file_dir=file_dir, mp4_file_name=video.title)




            

    # def test_watch(self, vid):
    #     self.driver.get(vid)
    #     wait = WebDriverWait(self.driver, 10)
    #     second_button = wait.until(
    #         EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'동영상 보기')]")))
    #     second_button.click()
    #     video_window = self.driver.window_handles[1]
    #     self.driver.switch_to.window(video_window)
    #     time.sleep(0.5)
    #     try:
    #         alert = self.driver.switch_to.alert
    #         alert.dismiss()
    #     except:
    #         pass
    #     main_window = self.driver.window_handles[0]

    #     self.driver.find_element(By.XPATH, '//*[@id="vod_player"]/div[2]/video').click()
    #     time.sleep(600)
    #     self.driver.quit()