"""
字体颜色设置
    url: https://www.jianshu.com/p/a6791ba66e3d

Wechaty模块
    url: https://wechaty.readthedocs.io/zh_CN/latest/references/wechaty/

itchat
    url: https://itchat.readthedocs.io/zh/latest/tutorial/tutorial0/

windnd
    url: https://github.com/cilame/windnd
"""
from tkinter import *
from tkinter import ttk


def t():
    for i in range(100):
        pb.step()
        print(pb["value"])
        root.update()
        root.after(10)


root = Tk()
pb = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=200, value=0, maximum=100.01)
pb.grid(column=1, row=0)
b = ttk.Button(root, text="start", command=t)
b.grid(column=0, row=0)

root.mainloop()
