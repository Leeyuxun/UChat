#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
通过安全信道传输的消息格式
|--Length of Message Body(4Bytes)--|--Length of AES padding (1Byte)--|--AES IV (16Bytes)--|--MAC (32Bytes)--|--Message Body (CSON)--|
"""

import math
import os
import socket
import struct
#from Crypto.Cipher import AES
from Cryptodome.Cipher import AES
import hashlib
from common.config import get_config
from common.cryptography import crypt
from common.message import serialize_message, deserialize_message, ByteArrayReader
from common.util import long_to_bytes
from pprint import pprint
from server.util import database

"""建立安全信道"""
class SecureChannel:

    def __init__(self, socket, shared_secret):
        socket.setblocking(0)
        self.socket = socket
        self.shared_secret = shared_secret
        return

    def send(self, message_type, parameters=None):
        iv1 = bytes(os.urandom(16))
        data_to_encrypt = serialize_message(message_type, parameters)
        length_of_message = len(data_to_encrypt)
        padding_n = math.ceil(length_of_message / 16) * 16 - length_of_message
        for i in range(0, padding_n):
            data_to_encrypt += b'\0'

        encryption_suite = AES.new(self.shared_secret, AES.MODE_CBC, iv1)
        encrypted_message = encryption_suite.encrypt(data_to_encrypt)
        length_of_encrypted_message = len(encrypted_message)

        # pprint([length_of_encrypted_message,
        #         struct.pack('L', length_of_encrypted_message), bytes([padding_n]), iv1, encrypted_message])
        # pprint(['sending', self.socket, message_type, parameters])
        mac = hashlib.md5(encrypted_message).hexdigest().encode()

        self.socket.send(
            struct.pack('!L', length_of_encrypted_message) + bytes([padding_n]) + iv1 + mac + encrypted_message)
        return

    def on_data(self, data_array):

        """用select循环socket.recv，当收到一个完整的数据块后（收到后length_of_encrypted_message+1+16+32个字节后），
        把 bytes([padding_n]) + iv1 + +mac + encrypted_message 传给本函数
		"""

        br = ByteArrayReader(data_array)

        # pprint(['recv', 'first_4_bytes', first_4_bytes, length_of_encrypted_message])
        padding_n = br.read(1)[0]
        # pprint(['recv', 'padding_n', padding_n])

        iv = br.read(16)
        # pprint(['recv', 'iv', iv])
        # incomplete
        bytes_received = 0

        # 对比接收到的mac值和用收到的加密数据算出的mac值是否相等
        recv_mac = br.read(32)
        data = br.read_to_end()
        mac = hashlib.md5(data).hexdigest().encode()
        if mac != recv_mac:
            pprint('Message Authentication Error')
            exit(-1)

        decryption_suite = AES.new(self.shared_secret, AES.MODE_CBC, iv)
        decrypted_data = decryption_suite.decrypt(data)

        if padding_n != 0:
            decrypted_data = decrypted_data[0:-padding_n]
        # pprint(['recv', 'decrypted_data', decrypted_data])

        return deserialize_message(decrypted_data)

    def close(self):
        self.socket.close()


def establish_secure_channel_to_server():
    config = get_config()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((config['client']['server_ip'], int(config['client']['server_port'])))

    # 获取本机IP
    ip = get_ip()
    s.send(ip.encode())

    # 接收服务器证书
    server_cert = s.recv(1024)

    certname = ip + "_cert.pem"
    if not os.path.exists(certname):
        # 生成私钥公钥和证书
        crypt.gen_secret()
        f = open('public.pem', 'rb')
        public = f.read()
        f.close()
        with open(certname, 'wb') as f:
            f.write("aaa bbb ".encode() + public)
            f.close()

    # 首次连接，给服务器发送证书
    with open(certname, 'rb') as f:
        client_cert = f.read()
        f.close()
    s.send(client_cert)

    their_secret = crypt.getpk_from_cert(server_cert)
    # 计算出共同密钥
    shared_secret = crypt.get_shared_secret(their_secret)

    sc = SecureChannel(s, shared_secret)

    return sc


def accept_client_to_secure_channel(socket):
    conn, addr = socket.accept()

    # 首次连接，客户端会发送diffle hellman密钥
    ip = conn.recv(1024)
    certname = ip + "_cert.pem".encode()

    # 把服务器的证书发送给客户端
    with open("admin_cert.pem", 'rb') as f:
        server_cert = f.read()
        f.close()

    conn.send(server_cert)

    client_cert = conn.recv(1024)
    with open(certname, 'wb') as f:
        f.write(client_cert)
        f.close()

    # 计算出共享密钥
    their_secret = crypt.getpk_from_cert(client_cert)
    shared_secert = crypt.get_shared_secret(their_secret)
    sc = SecureChannel(conn, shared_secert)

    return sc

"""获取本机IP"""
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    return ip