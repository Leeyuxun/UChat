#!/usr/bin/env python
# -*- coding:utf-8 -*-

from random import randint
from common.cryptography import prime
from common.config import get_config
from common.util import long_to_bytes
import hashlib

config = get_config()
base = config['crypto']['base']
modulus = config['crypto']['modulus']

"""生成公私钥并保存到文件中"""
def gen_secret():

    secret = prime.generate_big_prime(12)
    my_secret = base ** secret % modulus

    with open("private.pem", "wb") as f:
        f.write(str(secret).encode())
        f.close()
    with open("public.pem", "wb") as f:
        f.write(str(my_secret).encode())
        f.close()

"""生成共享密钥"""
def get_shared_secret(their_secret):

    with open("public.pem", "rb") as f:
        pub = f.read()
        f.close()

    f = open("private.pem", "rb")
    secret = int(f.read())
    f.close()
    return hashlib.sha256(long_to_bytes(int(their_secret) ** secret % modulus)).digest()

"""从证书中获取公钥"""
def getpk_from_cert(cert):

    str = cert.split()
    return str[2]