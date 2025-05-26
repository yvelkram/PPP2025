import tkinter
from tkinter import simpledialog
import time


def count_down(second: int, label: tkinter.Label, window: tkinter.Tk) -> None:
    def update():
        nonlocal second
        if second < 0:
            label.config(text=" vvvvvv\n"+"> BOOM <\n"+" ^^^^^^")
        else:
            label.config(text=f"{second}초...")
            window.after(1000, update)
            second -= 1
    update()


def main() -> None:
    main_window = tkinter.Tk()
    main_window.title("Count Down")

    second = simpledialog.askinteger("input", "초를 입력하세요")

    label = tkinter.Label(main_window, text="", font=("Arial", 24), width=20, height=5)
    label.pack(padx=20, pady=20)

    count_down(second, label, main_window)
    main_window.mainloop()


if __name__ == '__main__':
    main()
