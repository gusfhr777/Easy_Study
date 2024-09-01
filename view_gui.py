import tkinter as tk
from tkinter import ttk
import threading
import sys
import os
import time
import queue
import m3u8_To_MP4
from loggingInterface import log_print, report
from driverController import DriverController
from model import getLogQueue, Course, log_queue, VideoActivity
VERSION = 'v0.2.3a'
DATE = '2024-09-01(일)'
AUTHOR = '한국항공대학교 컴퓨터공학과'
TITLE = f'편한수강 {VERSION}'


# def backgroundTask():
    
#     if not Course.course_list:
#         isFirst = True
#     else:
#         isFirst = False
    
#     if dc.isAutoVideo:
#         watch(dc)
#         input('아무 키를 눌러 종료합니다.')
#         dc.driver.quit()
#         exit()

"""
해야할 일
영상 다운로드 기능
- m3u8 링크 가져오도록 crawlUnWatched 함수, model.VideoActivity 수정
- m3u8 to mp4 모듈 활용해서 m3u8 다운로드 함수 실행.
- 다운로드를 위한 GUI 인터페이스 제작 
- 테스트, 테스트, 테스트, .... 언제 다하냐
"""



        # while not log_queue.empty():
        #     log = log_queue.get()
        #     self.log_text.config(state=tk.NORMAL)
        #     self.log_text.insert(tk.END, log)
        #     self.log_text.see(tk.END)
        #     self.log_text.config(state=tk.DISABLED)

class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        pass

    def flush(self):
        pass  # `flush` 메서드는 파일 객체에서 필요하지만, 여기서는 빈 메서드로 유지

class Controller:
    def __init__(self):
        pass


class View():
    def __init__(self):
        self.dc = DriverController()
        self.normalizeFirst = True # variable for 3 buttons enabling
        Course.load()
        # Initialize main window
        self.root = tk.Tk()
        self.root.title(TITLE)
        self.root.geometry("400x500")
        try:
            self.root.iconbitmap("eagle.ico")
        except:pass
        log_print(f'편한수강 {VERSION}\n제작 : {AUTHOR}\n본 프로그램은 항공대 LMS 전용입니다.')

        self.isLoginString = tk.StringVar()
        self.state = tk.StringVar()
        self.isLoginString.set(f"{'로그인 완료' if self.dc.isLogin else '로그인 안됨'}")
        self.state.set('대기 중')

        # Create the main frame for log output and buttons
        self.main_frame = ttk.Frame(self.root, padding="5")
        self.main_frame.grid(row=0, column=0, sticky="NSEW")

        # Log output section
        # Log output section using a Text widget
        self.log_text = tk.Text(self.main_frame, wrap='word', bg='#f0f0f0', fg='#333333', font=('Helvetica', 10), state=tk.DISABLED, relief="solid", width=37, padx=10, pady=10, borderwidth=1)
        self.log_text.grid(row=0, column=0, rowspan=5, sticky="NSEW", padx=5, pady=5)
        sys.stdout = TextRedirector(self.log_text)

        # Variables section
        variables_frame = ttk.Frame(self.main_frame, relief="solid", padding="10")
        variables_frame.grid(row=0, column=1, sticky="NSEW", padx=5, pady=5)

        state_label = ttk.Label(variables_frame, textvariable=self.state, wraplength=100)
        state_label.grid(row=0, column=0, sticky="W")
        self.login_state_label = ttk.Label(variables_frame, textvariable=self.isLoginString)
        self.login_state_label.grid(row=1, column=0, sticky="W")

        # Buttons section
        self.button1 = ttk.Button(self.main_frame, text=f"LMS 불러오기", command=self.lmsCrawl)
        self.button2 = ttk.Button(self.main_frame, text=f"동영상 시청", command=self.openWatchWindow)
        self.button3 = ttk.Button(self.main_frame, text=f"동영상 다운로드", command=self.opendownloadWindow)
        self.button4 = ttk.Button(self.main_frame, text=f"데이터 출력", command=self.printCourseData)

        self.button1.config(state=tk.DISABLED)
        self.button2.config(state=tk.DISABLED)
        self.button3.config(state=tk.DISABLED)
        self.button4.config(state=tk.DISABLED)
        
        self.button1.grid(row=1, column=1, sticky="NSEW", padx=5, pady=5)
        self.button2.grid(row=2, column=1, sticky="NSEW", padx=5, pady=5)
        self.button3.grid(row=3, column=1, sticky="NSEW", padx=5, pady=5)
        self.button4.grid(row=4, column=1, sticky="NSEW", padx=5, pady=5)

        if Course.unwatched_video_list == []:
            self.button2.config(state=tk.DISABLED)

        # Option button
        # option_button = ttk.Button(self.main_frame, text="옵션")
        # option_button.grid(row=6, column=1, sticky="NSEW", padx=5, pady=5)
        # option_button.config(command=self.openOptionWindow)

        self.root.after(100, self.synchronize)
        self.root.mainloop()

    
    def synchronize(self): # model 데이터 동기화
        while not log_queue.empty():
            log = log_queue.get()
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, log)
            self.log_text.see(tk.END)  # 항상 스크롤을 최신 내용으로 유지
            self.log_text.config(state=tk.DISABLED)
        if self.dc.isLogin:
            self.isLoginString.set("로그인 완료")
        if self.dc.driver and self.normalizeFirst:
            self.button1.config(state=tk.NORMAL)
            if Course.unwatched_video_list:
                self.button2.config(state=tk.NORMAL)
            if Course.getAllActivityList(VideoActivity):
                self.button3.config(state=tk.NORMAL)

            self.button4.config(state=tk.NORMAL)
            self.normalizeFirst = False
        self.root.after(100, self.synchronize)
        

    def delOptionWindow(self): #옵션창 닫기
        self.dc.isAutoLogin = self.option_var1.get()
        self.options_window.destroy()
        

    def openOptionWindow(self): #옵션창 열기

        self.options_window = tk.Toplevel(self.root)
        self.options_window.title("옵션창")
        self.options_window.geometry("300x200")


        self.option_var1 = tk.BooleanVar()
        self.option_var1.set(self.dc.isAutoLogin)
        # option_var2 = tk.BooleanVar()
        # option_var3 = tk.BooleanVar()


        option1 = ttk.Checkbutton(self.options_window, text="자동 로그인 여부 ", variable=self.option_var1)
        option1.grid(row=0, column=0, sticky="W", padx=10, pady=5)

        # option2 = ttk.Checkbutton(options_window, text="자동시청 여부")
        # option2.grid(row=1, column=0, sticky="W", padx=10, pady=5)

        # option3 = ttk.Checkbutton(options_window, text="옵션3(체크버튼)")
        # option3.grid(row=2, column=0, sticky="W", padx=10, pady=5)

        confirm_button = ttk.Button(self.options_window, text="확인", command=self.delOptionWindow)
        confirm_button.grid(row=3, column=0, sticky="E", padx=10, pady=10)
        self.options_window.grab_set()
        

    def openWatchWindow(self): #동영상 시청 창 열기
        self.video_window = tk.Toplevel(self.root)
        self.video_window.title("동영상 시청")
        self.video_window.geometry("500x600")
        
        main_frame = ttk.Frame(self.video_window, relief="solid", padding=10)
        # main_frame.grid(row=0, column=0, padx=5, pady=5)
        main_frame.grid(row=0, column=0, padx=5, pady=5, sticky='n')
        # main_frame.pack()

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.watch_video_var_states = []

        for i, item in enumerate(Course.unwatched_video_list):
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(scrollable_frame, text=item.title, variable=var)
            cb.grid(row=i, column=0, sticky='w')
            self.watch_video_var_states.append(var)


        confirm_button = ttk.Button(self.video_window, text="확인", command=self.watch)
        confirm_button.grid(row=1, column=0, pady=10)
        # confirm_button.grid(row=1, column=0, pady=10)
        self.video_window.grab_set()

        # frame = ttk.Frame(main_frame, padding=10)
        # frame.grid(row=0, column=0, sticky="NSEW", padx=5, pady=5)
        # subframe = ttk.Frame(main_frame, padding="10")
        # subframe.grid(row=0, column=1, sticky="NSEW", padx=5, pady=5)
        
        # self.video_var_states = []
        # for video in Course.unwatched_video_list:
        #     var = tk.BooleanVar()
        #     var.set(True)
        #     label = ttk.Label(frame, text=video.title, anchor='w')
        #     label.pack(anchor='w', pady=5)
        #     chk = ttk.Checkbutton(subframe, text="", variable=var)
        #     chk.pack(anchor='e', pady=5)
        #     self.video_var_states.append(var)
        # confirm_button = ttk.Button(self.video_window, text="확인", command=self.watch)
        # confirm_button.pack(pady=10)
        # self.video_window.grab_set()

    def opendownloadWindow(self): #동영상 다운로드 창 열기
        self.download_window = tk.Toplevel(self.root)
        self.download_window.title("동영상 다운로드")
        self.download_window.geometry("500x600")
        
        main_frame = ttk.Frame(self.download_window, relief="solid", padding=10)
        # main_frame.grid(row=0, column=0, padx=5, pady=5)
        main_frame.grid(row=0, column=0, padx=5, pady=5, sticky='n')

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.download_video_var_states = []

        for i, item in enumerate(Course.getAllActivityList(VideoActivity)):
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(scrollable_frame, text=item.title, variable=var)
            cb.grid(row=i, column=0, sticky='w')
            self.download_video_var_states.append(var)



        # frame = ttk.Frame(main_frame, padding=10)
        # frame.grid(row=0, column=0, sticky="NSEW", padx=5, pady=5)
        # subframe = ttk.Frame(main_frame, padding="10")
        # subframe.grid(row=0, column=1, sticky="NSEW", padx=5, pady=5)
        
        # self.var_states = []
        # for video in Course.getAllActivityList(VideoActivity):
        #     var = tk.BooleanVar()
        #     var.set(True)
        #     label = ttk.Label(frame, text=video.title, anchor='w')
        #     label.pack(anchor='w', pady=5)
        #     chk = ttk.Checkbutton(subframe, text="", variable=var)
        #     chk.pack(anchor='e', pady=5)
        #     self.var_states.append(var)
        confirm_button = ttk.Button(self.download_window, text="확인", command=self.download)
        confirm_button.grid(row=1, column=0, pady=10)
        # confirm_button.grid(row=1, column=0, pady=10)
        self.download_window.grab_set()
    # def lmsLogin(self):
    #     def background():
    #         try:
    #             self.state.set('로그인 중')
    #             self.dc.login()
    #         except:
    #             report(reason='로그인 중 오류가 발생하였습니다. logs폴더와 함께 개발자에게 문의하세요.', driver=self.dc.driver)
    #     threading.Thread(target=background).start() 
    def lmsCrawl(self): #LMS 데이터 불러오기 버튼
        def background():
            try:
                self.button1.config(state=tk.DISABLED)
                self.state.set('목록 확인중')
                self.dc.crawlCourseList()
                self.state.set('강의 확인중')
                self.dc.crawlCourse()
                self.state.set('영상 확인중')
                self.dc.crawlUnWatched()
                self.state.set('대기 중')
                if Course.unwatched_video_list:
                    self.button2.config(state=tk.NORMAL)
                self.button1.config(state=tk.NORMAL)
                self.normalizeFirst = True
            except:
                report(reason='LMS 데이터를 불러오는 중 오류가 발생하였습니다. logs폴더와 함께 개발자에게 문의하세요.',driver=self.dc.driver)
        threading.Thread(target=background).start()

    def download(self):
        def background():
            try:
                self.state.set('다운로드 중')
                if not os.path.exists('./output/'):os.mkdir('./output/')
                log_print('\n동영상 다운로드를 시작합니다.')
                for i, video in enumerate(Course.getAllActivityList(VideoActivity)):
                    if not self.download_video_var_states[i].get(): continue
                    for course in Course.course_list:
                        if video in course.getActivityList(VideoActivity):
                            subject_name = course.title
                    file_dir = './output/' + subject_name + '/'
                    if not os.path.exists(file_dir):os.mkdir(file_dir)
                    log_print('다운로드 중 : '+video.title)
                    log_print(f"{video.m3u8}|{file_dir}|{video.title}")
                    m3u8_To_MP4.multithread_download(m3u8_uri=video.m3u8, mp4_file_dir=file_dir, mp4_file_name=video.title)
                log_print('모든 다운로드가 완료되었습니다.')
                self.state.set('대기 중')
            except:
                report('다운로드 중 오류가 발생하였습니다. logs폴더와 함꼐 개발자에게 문의하세요.')
        self.download_window.destroy()
        threading.Thread(target=background).start()

    def watch(self):
        def background():
            try:
                self.button2.config(state=tk.DISABLED)
                self.state.set('영상 시청 중')
                self.dc.watchUnwatchedVideo(self.watch_video_var_states)
                self.state.set('대기 중')
                self.button2.config(state=tk.NORMAL)
            except:
                report(reason='동영상 시청 중 오류가 발생하였습니다. logs폴더와 함께 개발자에게 문의하세요.',driver=self.dc.driver)
                
        self.video_window.destroy()
        threading.Thread(target=background).start()

    def printCourseData(self):
        if not os.path.exists('./output'):
            os.mkdir('./output')
        with open('output/CourseData.txt', 'w', encoding='utf-8') as f:
            f.write(Course.printCourse())
        log_print('output/CourseData.txt으로 출력을 완료하였습니다.')



def main():
    try:
        view = View()
    except:
        report()