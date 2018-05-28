from Crypto.Cipher import AES
import os
import struct
import sys


def encryption(plain_text):
    key_file = open("base_key.key", "r")
    key = key_file.read()
    encryption = AES.new(key[:32], AES.MODE_CBC, 'This is an IV456')
# encryption

# padding du plain_text pour qu'il ait une taille multiple de 16 byte
    while(len(plain_text)%16 != 0):
        plain_text += "".ljust(1, "\x00")
    cipher_text = encryption.encrypt(plain_text)
    return cipher_text

def decryption(cipher_text):
# decryption
    key_file = open("base_key.key", "r")
    key = key_file.read()
    decryption = AES.new(key[:32], AES.MODE_CBC, 'This is an IV456')
    decrypt_text = decryption.decrypt(cipher_text)
    print(decrypt_text)
# j'enleve le padding
    i = 0
    for c in decrypt_text:
        if(c=='\''):
            number = i
            break
        i += 1
    plain_text=decrypt_text[0:i].decode("utf-8")
    print(plain_text)
    return plain_text