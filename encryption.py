from Crypto.Cipher import AES
import os
import struct
import sys

# génération d'une clé de 16 bytes (necessaire pour l'encryption)
key = os.urandom(16)
print(key)
encryption = AES.new(key, AES.MODE_CBC, 'This is an IV456')

# padding du plain_text pour qu'il ait une taille multiple de 16 byte
plain_text = 'Antoine_le_bout'
while(len(plain_text)%16 != 0):
    plain_text += "".ljust(1, "\x00")
    print(plain_text)

# encryption
cipher_text = encryption.encrypt(plain_text)
print(cipher_text)

# decryption
decryption = AES.new(key, AES.MODE_CBC, 'This is an IV456')
decrypt_text = decryption.decrypt(cipher_text)
print(decrypt_text)

# j'enlève le padding
i = 0
for c in decrypt_text:
    if(c=='\''):
        number = i
        break
    i += 1
plain_text=decrypt_text[0:i].decode("utf-8")
print(plain_text)
