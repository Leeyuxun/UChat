#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""登录界面"""
import _tkinter
import sys
import tkinter as tk
from tkinter import messagebox
from common.message import MessageType
from pprint import pprint
import client.memory
from client.forms.register_form import RegisterForm
from client.forms.contacts_form import ContactsForm
import select
import _thread
import os
from tkinter import *
from tkinter import Toplevel
import client.util.socket_listener

"""登录界面"""
class LoginForm(tk.Frame):
    """ 关闭端口监听 """
    def remove_socket_listener_and_close(self):
        client.util.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()

    """" 关闭窗口 """
    def destroy_window(self):
        client.memory.tk_root.destroy()

    """ 开启监听 """
    def socket_listener(self, data):
        if data['type'] == MessageType.login_failed:
            messagebox.showerror('Error', '登入失败，请检查用户名密码')
            return

        if data['type'] == MessageType.login_successful:
            client.memory.current_user = data['parameters']
            self.remove_socket_listener_and_close()
            contacts = Toplevel(client.memory.tk_root, takefocus=True)
            ContactsForm(contacts)
            return

    def __init__(self, master=None):
        """创建主窗口用来容纳其他组件"""
        super().__init__(master)
        self.master = master
        self.master.title("Uchat——登录安全即时通信系统")
        self.master.resizable(width=False, height=False)
        self.master.geometry('480x300')
        # 画布放置图片
        self.canvas = tk.Canvas(self.master, width=480, height=300)
        self.image_file = tk.PhotoImage(file='client/forms/images/login_bg.gif')
        self.image = self.canvas.create_image(0, 0, anchor='nw', image=self.image_file)
        # 标签 用户名密码
        self.user_name = tk.Label(self.master, text='用户名', font=("楷体", 16), fg="black", bg="#35d1e9")
        self.user_pwd = tk.Label(self.master, text='密  码', font=("楷体", 16), fg="black", bg="#43d5eb")
        # 用户名输入框
        self.var_user_name = tk.StringVar()
        self.entry_user_name = tk.Entry(self.master, textvariable=self.var_user_name, font=("楷体", 18), fg="black",
                                        bg="#4fd8ec", relief=GROOVE)
        # 密码输入框
        self.var_user_pwd = tk.StringVar()
        self.entry_user_pwd = tk.Entry(self.master, textvariable=self.var_user_pwd, show='* ', font=("楷体", 18),
                                       fg="black", bg="#4ed6e8", relief=GROOVE)
        # 登录 注册按钮
        self.register_btn = tk.Button(self.master, text='注册', font=("楷体", 18), fg="black", bg="#6cdcf0",
                                      activebackground="#6cdcf0", relief=GROOVE, command=self.show_register)
        self.login_btn = Button(self.master, text='登录', font=("楷体", 18), fg="black", bg="#6cdcf0",
                                activebackground="#6cdcf0", relief=GROOVE, command=self.do_login)
        self.quit_btn = tk.Button(self.master, text='退出', font=("楷体", 18), fg="black", bg="#3fd4e7",
                                  activebackground="#6cdcf0", relief=GROOVE, command=self.destroy_window)
        # 位置定位
        self.canvas.grid(row=0, column=0, rowspan=7, columnspan=8, )
        self.user_name.grid(row=4, column=2, sticky=E, padx=0, pady=0, )
        self.user_pwd.grid(row=5, column=2, sticky=E + N)
        self.entry_user_name.grid(row=4, column=3, columnspan=2, sticky=W)
        self.entry_user_pwd.grid(row=5, column=3, columnspan=2, sticky=W + N)
        self.register_btn.grid(row=6, column=2, columnspan=1, sticky=E + N)
        self.login_btn.grid(row=6, column=3, columnspan=1, sticky=E + N)
        self.quit_btn.grid(row=6, column=4, columnspan=1, sticky=E + N)
        self.sc = client.memory.sc
        client.util.socket_listener.add_listener(self.socket_listener)

    """ 登陆操作 """
    def do_login(self):
        """登录操作若为空则提示用户错误"""
        username = self.var_user_name.get()
        password = self.var_user_pwd.get()
        if not username:
            messagebox.showerror("Error", "用户名不能为空", )
            return
        if not password:
            messagebox.showerror("Error", "密码不能为空")
            return
        self.sc.send(MessageType.login, [username, password])

    """ 转到注册界面 """
    def show_register(self):
        register_form = Toplevel()
        RegisterForm(register_form)