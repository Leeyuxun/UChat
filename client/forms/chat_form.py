#!/usr/bin/env python
# -*- coding:utf-8 -*-

""""聊天界面及处理与聊天相关的事件"""
import tkinter as tk
from tkinter import *
import client.memory
from client.util.socket_listener import *
from tkinter.scrolledtext import ScrolledText
from tkinter import colorchooser
from tkinter import simpledialog
from tkinter import filedialog
from PIL import Image, ImageTk
from io import BytesIO
from client.util import socket_listener
import binascii
import time
import filetype
import os

"""创建聊天框"""
class ChatForm(tk.Frame):

    font_color = "#000000"
    font_size = 16
    user_list = []
    tag_i = 0

    """将监听事件移除并关闭该窗口"""
    def remove_listener_and_close(self):
        remove_message_listener(self.message_listener)
        client.util.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()
        if self.target['id'] in client.memory.window_instance[self.target['type']]:
            del client.memory.window_instance[self.target['type']][self.target['id']]

    """定义监听事件"""
    def message_listener(self, data):
        self.digest_message(data)

    """监听socket传来的数据"""
    def socket_listener(self, data):
        init_time = int(time.time())
        dirname = "send_msg_log"
        filename = str(init_time)
        dir_flag = os.path.exists(dirname)
        if dir_flag == False:
            os.mkdir(dirname)
        if data['parameters']['message']['type'] == 1:
            with open(dirname + '/' + filename, 'wb') as f:
                contents = data['parameters']['message']['data']
                f.write(contents)
                f.close()
            with open(dirname + '/' + filename, 'rb') as f:
                file_format = filetype.guess(dirname + '/' + filename)
                file_format = file_format.extension
                if file_format == None:
                    file_format = "txt"
                f.close()
            os.rename(dirname + '/' + filename, (str(dirname + '/' + filename) + '_.' + file_format))
        if data['type'] == MessageType.query_room_users_result:
            if data['parameters'][1] != self.target['id']:
                return
            self.user_list = data['parameters'][0]
            self.refresh_user_listbox()
        if data['type'] == MessageType.room_user_on_off_line:
            if data['parameters'][0] != self.target['id']:
                return
            for i in range(0, len(self.user_list)):
                if self.user_list[i][0] == data['parameters'][1]:
                    self.user_list[i][2] = data['parameters'][2]
            self.refresh_user_listbox()

    """更新好友列表"""
    def refresh_user_listbox(self):
        self.user_listbox.delete(0, END)
        self.user_list.sort(key=lambda x: x[2])
        for user in self.user_list:
            self.user_listbox.insert(0, user[1] + ("(在线)" if user[2] else "(离线)"))
            self.user_listbox.itemconfig(0, {'fg': ("blue" if user[2] else "#505050")})

    """处理消息并将其展示出来"""
    def digest_message(self, data):
        time = datetime.datetime.fromtimestamp(
            int(data['time']) / 1000
        ).strftime('%Y-%m-%d %H:%M:%S')
        self.append_to_chat_box(data['sender_name'] + "  " + time + '\n',
                                ('me' if client.memory.current_user['id'] == data[
                                    'sender_id'] else 'them'))
        # type 0 - 文字消息 1 - 图片消息
        if data['message']['type'] == 0:
            self.tag_i += 1
            self.chat_box.tag_config('new' + str(self.tag_i),
                                     lmargin1=16,
                                     lmargin2=16,
                                     foreground=data['message']['fontcolor'],
                                     font=(None, data['message']['fontsize']))
            self.append_to_chat_box(data['message']['data'] + '\n',
                                    'new' + str(self.tag_i))
        if data['message']['type'] == 1:
            client.memory.tk_img_ref.append(ImageTk.PhotoImage(data=data['message']['data']))
            self.chat_box.image_create(END, image=client.memory.tk_img_ref[-1], padx=16, pady=5)
            self.append_to_chat_box('\n', '')

    """ 双击聊天框 """
    def user_listbox_double_click(self, _):
        if len(self.user_listbox.curselection()) == 0:
            return None
        index = self.user_listbox.curselection()[0]
        selected_user_id = self.user_list[len(self.user_list) - 1 - index][0]
        selected_user_username = self.user_list[len(self.user_list) - 1 - index][3]
        if selected_user_id == client.memory.current_user['id']:
            return
        client.memory.contact_window[0].try_open_user_id(selected_user_id,
                                                         selected_user_username)
        return

    def __init__(self, target, master=None):
        super().__init__(master)
        self.master = master
        self.target = target
        self.user_listbox = tk.Listbox(self, bg='#63d5eb', width=0, bd=0)
        client.util.socket_listener.add_listener(self.socket_listener)
        client.memory.unread_message_count[self.target['type']][self.target['id']] = 0
        client.memory.contact_window[0].refresh_contacts()
        master.resizable(width=False, height=False)
        master.geometry('580x500')
        self.sc = client.memory.sc
        # 私人聊天
        if self.target['type'] == 0:
            self.master.title(self.target['username'])
        # 群组聊天
        if self.target['type'] == 1:
            self.master.title("[群:" + str(self.target['id']) + "] " + self.target['room_name'])
            self.sc.send(MessageType.query_room_users, self.target['id'])

        self.right_frame = tk.Frame(self)

        self.user_listbox.bind('<Double-Button-1>', self.user_listbox_double_click)
        if self.target['type'] == 1:
            self.user_listbox.pack(side=LEFT, expand=False, fill=BOTH)

        self.right_frame.pack(side=LEFT, expand=True, fill=BOTH)
        self.input_frame = tk.Frame(self.right_frame, bg='#63d5eb')
        self.input_textbox = ScrolledText(self.right_frame, bg='#63d5eb', font=("楷书", 16), height=5)
        self.input_textbox.bind("<Control-Return>", self.send_message)
        self.input_textbox.bind_all('<Key>', self.apply_font_change)
        self.send_btn = tk.Button(self.input_frame, text='发送消息(Ctrl+Enter)', font=("仿宋", 16, 'bold'), fg="black",
                                  bg="#35d1e9",activebackground="#6cdcf0", relief=GROOVE, command=self.send_message)
        self.send_btn.pack(side=RIGHT, expand=False)
        self.font_btn = tk.Button(self.input_frame, text='字体颜色', font=("仿宋", 16, 'bold'), fg="black", bg="#35d1e9",
                                  activebackground="#6cdcf0", relief=GROOVE, command=self.choose_color)
        self.font_btn.pack(side=LEFT, expand=False)
        self.font_btn = tk.Button(self.input_frame, text='字体大小', font=("仿宋", 16, 'bold'), fg="black", bg="#35d1e9",
                                  activebackground="#6cdcf0", relief=GROOVE, command=self.choose_font_size)
        self.font_btn.pack(side=LEFT, expand=False)
        self.image_btn = tk.Button(self.input_frame, text='发送文件', font=("仿宋", 16, 'bold'), fg="black", bg="#35d1e9",
                                   activebackground="#6cdcf0", relief=GROOVE, command=self.send_image)
        self.image_btn.pack(side=LEFT, expand=False)
        self.chat_box = ScrolledText(self.right_frame, bg='#70d5eb')
        self.input_frame.pack(side=BOTTOM, fill=X, expand=False)
        self.input_textbox.pack(side=BOTTOM, fill=X, expand=False, padx=(0, 0), pady=(0, 0))
        self.chat_box.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.chat_box.bind("<Key>", lambda e: "break")
        self.chat_box.tag_config("default", lmargin1=10, lmargin2=10, rmargin=10, font=("仿宋", 15))
        self.chat_box.tag_config("me", foreground="green", spacing1='0', font=("仿宋", 15))
        self.chat_box.tag_config("them", foreground="blue", spacing1='0', font=("仿宋", 15))
        self.chat_box.tag_config("message", foreground="black", spacing1='0', font=("楷体", 15))
        self.chat_box.tag_config("system", foreground="#505050", spacing1='0', justify='center', font=("新宋体", 10))

        self.pack(expand=True, fill=BOTH)

        add_message_listener(self.target['type'], self.target['id'], self.message_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_listener_and_close)

        # 历史消息显示
        if target['id'] in client.memory.chat_history[self.target['type']]:
            for msg in client.memory.chat_history[self.target['type']][target['id']]:
                self.digest_message(msg)

            self.append_to_chat_box('- 以上是历史消息 -\n', 'system')

    """ 附加聊天框 """
    def append_to_chat_box(self, message, tags):
        self.chat_box.insert(tk.END, message, [tags, 'default'])
        self.chat_box.update()
        self.chat_box.see(tk.END)

    """ 发送消息 """
    def send_message(self, _=None):
        message = self.input_textbox.get("1.0", END)
        if not message or message.replace(" ", "").replace("\r", "").replace("\n", "") == '':
            return
        self.sc.send(MessageType.send_message,
                     {'target_type': self.target['type'], 'target_id': self.target['id'],
                      'message': {
                          'type': 0,
                          'data': message.strip().strip('\n'),
                          'fontsize': self.font_size,
                          'fontcolor': self.font_color
                      }
                      })
        self.input_textbox.delete("1.0", END)
        return 'break'

    """ 选择字体颜色 """
    def choose_color(self):
        _, self.font_color = colorchooser.askcolor(initialcolor=self.font_color)
        self.apply_font_change(None)

    """ 选择字体大小 """
    def choose_font_size(self):
        result = simpledialog.askinteger("设置", "请输入字体大小", initialvalue=self.font_size)
        if result is None:
            return
        self.font_size = result
        self.apply_font_change(None)

    """" 更新字体 """
    def apply_font_change(self, _):
        try:
            self.input_textbox.tag_config('new', foreground=self.font_color, font=(None, self.font_size))
            self.input_textbox.tag_add('new', '1.0', END)
        except:
            pass

    """" 发送图片 """
    def send_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Image Files",
                                                          ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.JPG", "*.JPEG",
                                                           "*.PNG", "*.GIF"]),
                                                         ("All Files", ["*.*"])])
        if filename is None or filename == '':
            return
        with open(filename, "rb") as imageFile:
            f = imageFile.read()
            b = bytearray(f)
            self.sc.send(MessageType.send_message,
                         {'target_type': self.target['type'], 'target_id': self.target['id'],
                          'message': {'type': 1, 'data': b}})
