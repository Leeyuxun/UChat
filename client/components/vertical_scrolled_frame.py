#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""Tkinter可滚动框架"""
import tkinter as tk
from tkinter import *


class VerticalScrolledFrame(Frame):
    """一个真正工作的纯Tkinter可滚动框架!"""
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # 创建一个画布对象和一个垂直滚动条来滚动它
        self.vscrollbar = Scrollbar(self, background="#43d5eb", orient=VERTICAL)
        self.vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)

        # 画布背景
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=self.vscrollbar.set)
        self.image_file = tk.PhotoImage(file='client/forms/images/VerticalScrolled.png')
        self.image = self.canvas.create_image(0, 0, anchor='nw', image=self.image_file)

        # 定位画布位置
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        self.vscrollbar.config(command=self.canvas.yview)

        # 重置视图
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # 在画布内创建一个框架，该框架将与画布一起滚动
        self.interior = interior = Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=interior, anchor=NW)

        # 跟踪画布和框架宽度的变化并同步，同时更新滚动条
        def _configure_interior(event):
            # 更新滚动条以匹配内部框架的大小
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # 更新画布的宽度以适应内部框架
                self.canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # 更新内部框架的宽度以填充画布
                self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

        self.canvas.bind('<Configure>', _configure_canvas)

        return