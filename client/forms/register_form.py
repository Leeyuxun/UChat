#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _tkinter
import tkinter as tk
from tkinter import ttk
from common.transmission.secure_channel import establish_secure_channel_to_server
from tkinter import messagebox
from common.message import MessageType
from pprint import pprint
from client.memory import current_user
from common.transmission.secure_channel import get_ip
import select
import client.util.socket_listener
from common.config import get_config
import client.memory
import socket
from tkinter import *
from tkinter import Toplevel
import re

""" 注册操作 """
class RegisterForm(tk.Frame):
    """ 打开事件监听 """
    def socket_listener(self, data):
        if data['type'] == MessageType.username_taken:
            messagebox.showerror('Error', '用户名已被使用，请换一个')
            return

        if data['type'] == MessageType.register_successful:
            messagebox.showinfo('Congratulations', '恭喜，注册成功，您成为第' + str(data['parameters'])+'个用户')
            self.remove_socket_listener_and_close()
            return

    """ 关闭监听 """
    def remove_socket_listener_and_close(self):
        client.util.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.sc = client.memory.sc

        self.master.title("Uchat——注册")
        master.resizable(width=False, height=False)
        master.geometry('480x500')
        # 画布
        self.canvas = tk.Canvas(self.master, width=480, height=500)
        self.image_file = tk.PhotoImage(file='client/forms/images/register_bg.gif')
        self.image = self.canvas.create_image(0, 0, anchor='nw', image=self.image_file)
        # 标签 用户名、密码、确认密码、邮箱、性别、年龄
        self.user_name = tk.Label(self.master, text="用户名", font=("楷体", 16), fg="black", bg="#30cfe8")
        self.user_pwd = tk.Label(self.master, text="密  码", font=("楷体", 16), fg="black", bg="#32d0ea")
        self.confirm_pwd = tk.Label(self.master, text="确认密码", font=("楷体", 16), fg="black", bg="#3ad2e9")
        self.user_email = tk.Label(self.master, text="邮  箱", font=("楷体", 16), fg="black", bg="#58daec")
        self.user_sex = tk.Label(self.master, text="性  别", font=("楷体", 16), fg="black", bg="#5bdbec")
        self.user_age = tk.Label(self.master, text="年  龄", font=("楷体", 16), fg="black", bg="#5bdbec")
        # 输入框
        # 用户名输入框
        self.var_user_name = tk.StringVar()
        self.entry_user_name = tk.Entry(self.master, textvariable=self.var_user_name, font=("楷体", 18), fg="black",
                                        bg="#4ed8eb", relief=GROOVE)
        # 密码输入框
        self.var_user_pwd = tk.StringVar()
        self.entry_user_pwd = tk.Entry(self.master, textvariable=self.var_user_pwd, show='* ', font=("楷体", 18),
                                       fg="black", bg="#48d7ec", relief=GROOVE)
        # 确认密码输入框
        self.var_confirm_pwd = tk.StringVar()
        self.entry_confirm_pwd = tk.Entry(self.master, textvariable=self.var_confirm_pwd, show='* ', font=("楷体", 18),
                                          fg="black", bg="#54d9ec", relief=GROOVE)
        # 邮箱输入框
        self.var_user_email = tk.StringVar()
        self.entry_user_email = tk.Entry(self.master, textvariable=self.var_user_email, font=("Arial", 14), fg="black",
                                         bg="#59d8ee", relief=GROOVE)
        # 性别输入框
        self.var_user_sex = tk.StringVar()
        self.entry_user_sex = ttk.Combobox(self.master, textvariable=self.var_user_sex, font=("楷体", 18),
                                           state="readonly")
        self.entry_user_sex['values'] = ("保密", "男", "女")
        self.entry_user_sex.current(0)
        # 年龄输入框
        self.var_user_age = tk.StringVar()
        self.entry_user_age = ttk.Combobox(self.master, textvariable=self.var_user_age, font=("楷体", 18),
                                           state="readonly")
        self.entry_user_age['values'] = ("保密", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                                         21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
                                         41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
                                         61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
                                         81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99,
                                         100)
        self.entry_user_age.current(0)
        # 注册按钮
        self.register_btn = tk.Button(self.master, text='       注     册       ', font=("楷体", 18), fg="black",
                                      bg="#5edbee", activebackground="#61d8ee", relief=GROOVE, width=30,
                                      command=self.do_register)
        # 位置定位
        # label位置定位
        self.canvas.grid(row=0, column=0, rowspan=18, columnspan=8, )
        self.user_name.grid(row=8, column=1, columnspan=2, sticky=E)
        self.user_pwd.grid(row=9, column=1, columnspan=2, sticky=E)
        self.confirm_pwd.grid(row=10, column=1, columnspan=2, sticky=E)
        self.user_email.grid(row=11, column=1, columnspan=2, sticky=E)
        self.user_sex.grid(row=12, column=1, columnspan=2, sticky=E)
        self.user_age.grid(row=13, column=1, columnspan=2, sticky=E)
        # 输入框位置定位
        self.entry_user_name.grid(row=8, column=3, columnspan=3, sticky=W, )
        self.entry_user_pwd.grid(row=9, column=3, columnspan=3, sticky=W, )
        self.entry_confirm_pwd.grid(row=10, column=3, columnspan=3, sticky=W, )
        self.entry_user_email.grid(row=11, column=3, columnspan=3, sticky=W, )
        self.entry_user_sex.grid(row=12, column=3, columnspan=3, sticky=W, )
        self.entry_user_age.grid(row=13, column=3, columnspan=3, sticky=W, )
        # 注册按钮位置定位
        self.register_btn.grid(row=14, column=2, columnspan=4, sticky=S + W)
        # 设置下拉框背景
        self.combo_style = tk.ttk.Style()
        self.combo_style.theme_create('self.combo_style', parent='alt',
                                      settings={'TCombobox':
                                                    {'configure':
                                                         {'foreground': 'black',
                                                          'selectbackground': '#60d8ee',
                                                          'fieldbackground': '#60d8ee',
                                                          'background': '#60d8ee',

                                                          }
                                                     }
                                                }
                                      )
        self.combo_style.theme_use('self.combo_style')

        self.sc = client.memory.sc
        client.util.socket_listener.add_listener(self.socket_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_socket_listener_and_close)

    """" 注册操作 """
    def do_register(self):

        username = self.var_user_name.get()
       # print(type(username).__name__)
        password = self.var_user_pwd.get()
        #print(type(password).__name__)
        password_confirmation = self.var_confirm_pwd.get()
        email = self.var_user_email.get()
        #print(type(email).__name__)
        sex = self.var_user_sex.get()
        #print(type(sex).__name__)
        age = self.var_user_age.get()
        #print(type(age).__name__)

        ip = get_ip()
        #print(type(ip).__name__)
        config = get_config()
        port = str((config['client']['client_port']))
        #print(type(port).__name__)

        if not username:
            messagebox.showerror("Error", "用户名不能为空")
            return
        if not email:
            messagebox.showerror("Error", "邮箱不能为空")
            return
        if not password:
            messagebox.showerror("Error", "密码不能为空")
            return
        if password != password_confirmation:
            messagebox.showerror("Error", "两次密码输入不一致")
            return
        if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$',email):
            messagebox.showerror("Error", "邮箱格式错误")
            return
        self.sc.send(MessageType.register, [username, password, email, ip, port, sex, age])

        certname = ip + "_cert.pem"
        with open(certname, 'rb') as f:
            context = f.read()
            sp = context.split()
            f.close()
        with open(certname,'wb') as f:
            f.write((str(self.var_user_name.get()) + ' ' + str(self.var_user_email.get()) + " " + str(sp[2])).encode())
            f.close()
        #with open(certname, "rb") as f:
            #a = f.read()
           # print("content_after_write!!!:is:", a)
            #f.close()
