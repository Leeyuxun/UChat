#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""联系人列表 UI"""
from tkinter import *
from pprint import pprint

""""联系人界面"""
class ContactItem(Frame):

    def __init__(self, parent, onclick):
        Frame.__init__(self, parent)

        def handle_on_click(e):
            e.widget = self
            onclick(e)

        Frame.config(self, bg="#43d5eb", borderwidth=2, relief=GROOVE)

        # == Line 1
        self.title_frame = Frame(self, bg="#43d5eb")
        self.last_message_time_frame = Frame(self, bg="#43d5eb")
        self.friend_ip_frame = Frame(self, bg="#43d5eb")
        self.message_frame = Frame(self, bg="#43d5eb")

        # last_message
        self.message_frame.pack(side=BOTTOM, fill=BOTH, expand=True, pady=(0, 5), padx=3)
        self.last_message = Label(self.message_frame, text="recent message", font=('新宋体', 13), fg='black', bg="#43d5eb")
        self.last_message.pack(side=LEFT, fill=X, expand=True, anchor=W)

        # title
        self.title_frame.pack(side=LEFT, fill=BOTH, expand=True, anchor=W, pady=(1, 1), padx=3)
        self.title = Label(self.title_frame, text="Title", font=("仿宋", 15, 'bold'), bg="#43d5eb")
        self.title.pack(side=LEFT, fill=None, anchor=W)

        # 最后一条消息的时间
        self.last_message_time_frame.pack(side=TOP, expand=FALSE, fill=BOTH)
        self.last_message_time = Label(self.last_message_time_frame, text="date", font=('仿宋', 10), fg='#575757', bg="#43d5eb")
        self.last_message_time.pack(side=RIGHT, anchor=E)

        # 好友的ip
        self.friend_ip_frame.pack(side=TOP, expand=FALSE, fill=BOTH)
        self.friend_ip = Label(self.friend_ip_frame, text="ip", font=('仿宋', 10), fg='#575757', bg="#43d5eb")
        self.friend_ip.pack(side=RIGHT, anchor=E)

        # 处理未读消息
        self.unread_message_count = Label(self.message_frame, text="0", font=('Arial', 10), fg='white', bg='red')
        self.unread_message_count.pack(side=RIGHT, anchor=E, fill=None, expand=False, ipadx=2)
        self.unread_message_count.pack_forget()

        # 将单击事件传输到父级
        self.title.bind("<Button>", handle_on_click)
        self.last_message_time.bind("<Button>", handle_on_click)
        self.last_message.bind("<Button>", handle_on_click)
        self.unread_message_count.bind("<Button>", handle_on_click)
        self.message_frame.bind("<Button>", handle_on_click)
        self.title_frame.bind("<Button>", handle_on_click)

        self.pack()

        return
