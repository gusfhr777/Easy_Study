import tkinter as tk
from tkinter import ttk
import threading
import sys
import os
import time
import queue
from loggingInterface import log_print, report
from driverController import DriverController
from model import getLogQueue, Course
VERSION = 'v0.2.1a'
DATE = '2024-06-23(일)'
AUTHOR = '한국항공대학교 컴퓨터공학과'
TITLE = f'편한수강 {VERSION}'
state = '실행 중'



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


class View:
    def __init__(self):
        self.dc = DriverController()
        self.state = '로딩중'
        Course.load()
        # Initialize main window
        self.root = tk.Tk()
        self.root.title(TITLE)
        self.root.geometry("400x500")

        # Create the main frame for log output and buttons
        self.main_frame = ttk.Frame(self.root, padding="5")
        self.main_frame.grid(row=0, column=0, sticky="NSEW")

        # Log output section
        # Log output section using a Text widget
        self.log_text = tk.Text(self.main_frame, wrap='word', state=tk.DISABLED, relief="solid", width=40)
        self.log_text.grid(row=0, column=0, rowspan=5, sticky="NSEW", padx=5, pady=5)

        # Variables section
        variables_frame = ttk.Frame(self.main_frame, relief="solid", padding="10")
        variables_frame.grid(row=0, column=1, sticky="NSEW", padx=5, pady=5)

        state_label = ttk.Label(variables_frame, text=self.state)
        state_label.grid(row=0, column=0, sticky="W")
        login_state_label = ttk.Label(variables_frame, text=f"{'로그인 완료' if self.dc.isLogin else '로그인 안됨'}")
        login_state_label.grid(row=1, column=0, sticky="W")

        # Buttons section
        self.button1 = ttk.Button(self.main_frame, text=f"LMS 불러오기", command=self.lmsCrawl)
        self.button1.grid(row=1, column=1, sticky="NSEW", padx=5, pady=5)
        self.button2 = ttk.Button(self.main_frame, text=f"동영상 시청", command=self.openVideoWatchOption)
        self.button2.grid(row=2, column=1, sticky="NSEW", padx=5, pady=5)
        self.button3 = ttk.Button(self.main_frame, text=f"데이터 출력", command=self.printCourseData)
        self.button3.grid(row=3, column=1, sticky="NSEW", padx=5, pady=5)

        if Course.unwatched_video_list == []:
            self.button2.config(state=tk.DISABLED)

        # Option button
        option_button = ttk.Button(self.main_frame, text="옵션")
        option_button.grid(row=6, column=1, sticky="NSEW", padx=5, pady=5)
        option_button.config(command=self.openOptionWindow)

        self.root.after(100, self.synchronize)
        self.root.mainloop()

    
    def synchronize(self): # model 데이터 동기화
        log_queue = getLogQueue()
        if log_queue:
            self.log_text.config(state=tk.NORMAL)
            for log in log_queue:
                self.log_text.insert(tk.END, log + '\n')
            self.log_text.config(state=tk.DISABLED)
        self.root.after(100, self.synchronize)
    
    def lmsCrawl(self):
        self.state = '로그인 중'
        self.dc.login()
        self.state = '강의 목록 확인중'
        self.dc.crawlCourseList()
        self.state = '강의 확인중'
        self.dc.crawlCourse()
        self.state = '안 본 영상 확인중'
        self.dc.crawlUnWatched()
        if Course.unwatched_video_list:
            self.button2.config(state=tk.NORMAL)
        

    def delOptionWindow(self):
        self.dc.isAutoLogin = self.option_var1

        self.options_window.destroy()
        

    def openOptionWindow(self):

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

    def openVideoWatchOption(self):
        video_window = tk.Toplevel(self.root)
        video_window.title("동영상 시청")
        video_window.geometry("300x200")

        frame = ttk.Frame(video_window, padding=20)
        frame.pack()
        subframe = ttk.Frame(frame)
        subframe.pack(side=tk.RIGHT)
        
        var_states = []
        for video in Course.unwatched_video_list:
            var = tk.BooleanVar()
            var.set(True)
            var_states.append(var)
            label = ttk.Label(frame, text=video.title, anchor='w', width=15)
            label.pack(anchor='w', pady=5)
            
            chk = ttk.Checkbutton(subframe, text='', variable=var)
            chk.pack(anchor='e', pady=5)
        confirm_button = ttk.Button(video_window, text="확인", command=self.watch)
        confirm_button.pack(pady=10)

    def watch(self):
        self.state = '안 본 영상 시청 중'
        self.dc.watchUnwatchedVideo()
        self.state = '유휴 상태'

    def printCourseData(self):
        if not os.path.exists('./output'):
            os.mkdir('./output')
        with open('output/CourseData.txt', 'w', encoding='utf-8') as f:
            f.write(Course.printCourse())
        log_print('output/CourseData.txt으로 출력을 완료하였습니다.')



def main():
    view = View()