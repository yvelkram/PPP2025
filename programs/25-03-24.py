import tkinter
import tkinter.simpledialog

import rich



window = tkinter.Tk()
window.withdraw()

text = "hello, world!"
a = tkinter.simpledialog.askstring(title = "test", prompt=text)

print(a)


rich.print("Hello, [bold magenta]World[/bold magenta]!", ":vampire:")

