import tkinter as tk
import threading
import time
import queue

# 백그라운드 작업
def background_task(q):
    for i in range(5):
        time.sleep(1)
        q.put(f"Task step {i+1}")
    q.put("Task completed")

# 버튼 클릭 이벤트 핸들러
def start_background_task():
    thread = threading.Thread(target=background_task, args=(task_queue,))
    thread.start()
    root.after(100, process_queue)

# 큐 처리 함수
def process_queue():
    try:
        msg = task_queue.get_nowait()
        status_label.config(text=msg)
    except queue.Empty:
        pass
    finally:
        root.after(100, process_queue)

# GUI 코드
def create_gui():
    global root, status_label, task_queue
    root = tk.Tk()
    root.title("Tkinter Background Task Example")

    # 버튼 생성 및 이벤트 핸들러 연결
    start_button = tk.Button(root, text="Start Background Task", command=start_background_task)
    start_button.pack(pady=20)

    # 상태 레이블 생성
    status_label = tk.Label(root, text="Press the button to start the task")
    status_label.pack(pady=20)

    # 큐 생성
    task_queue = queue.Queue()

    # GUI 이벤트 루프 실행
    root.mainloop()

# 메인 함수
if __name__ == "__main__":
    create_gui()
