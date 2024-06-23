import tkinter as tk
from tkinter import ttk

# Initialize main window
root = tk.Tk()
root.title("메인창")
root.geometry("800x600")  # You can adjust the size accordingly

# Create the main frame for log output and buttons
main_frame = ttk.Frame(root, padding="5")
main_frame.grid(row=0, column=0, sticky="NSEW")

# Log output section
log_label = ttk.Label(main_frame, text="로그 출력부분", relief="solid", padding="10")
log_label.grid(row=0, column=0, rowspan=6, sticky="NSEW", padx=5, pady=5)

# Variables section
variables_frame = ttk.Frame(main_frame, relief="solid", padding="10")
variables_frame.grid(row=0, column=1, sticky="NSEW", padx=5, pady=5)

a_label = ttk.Label(variables_frame, text="a = 3")
a_label.grid(row=0, column=0, sticky="W")
b_label = ttk.Label(variables_frame, text="b = 4")
b_label.grid(row=1, column=0, sticky="W")
c_label = ttk.Label(variables_frame, text="c = 4")
c_label.grid(row=2, column=0, sticky="W")

# Buttons section
for i in range(1, 6):
    button = ttk.Button(main_frame, text=f"버튼 {i}")
    button.grid(row=i, column=1, sticky="NSEW", padx=5, pady=5)

# Option button
option_button = ttk.Button(main_frame, text="옵션")
option_button.grid(row=6, column=1, sticky="NSEW", padx=5, pady=5)

# Options window
def open_options_window():
    options_window = tk.Toplevel(root)
    options_window.title("옵션창")
    options_window.geometry("300x200")

    option1 = ttk.Checkbutton(options_window, text="옵션 1(체크버튼)")
    option1.grid(row=0, column=0, sticky="W", padx=10, pady=5)

    option2 = ttk.Checkbutton(options_window, text="옵션2(체크버튼)")
    option2.grid(row=1, column=0, sticky="W", padx=10, pady=5)

    option3 = ttk.Checkbutton(options_window, text="옵션3(체크버튼)")
    option3.grid(row=2, column=0, sticky="W", padx=10, pady=5)

    confirm_button = ttk.Button(options_window, text="확인")
    confirm_button.grid(row=3, column=0, sticky="E", padx=10, pady=10)

option_button.config(command=open_options_window)

root.mainloop()