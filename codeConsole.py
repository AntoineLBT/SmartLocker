
import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import Adafruit_CharLCD as LCD

from Crypto.Cipher import AES
import os
import struct
import sys

# configuration de l'ecran

# Raspberry Pi pin configuration:
lcd_rs        = 26  # Note this might need to be changed to 21 for older revision Pi's.
lcd_en        = 24
lcd_d4        = 23
lcd_d5        = 17
lcd_d6        = 18
lcd_d7        = 22
lcd_backlight = 4

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2

# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)


continue_reading = True

# Fonction de decryption

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

# padding du plain_text pour qu'il ait une taille multiple de 16 byte

def padding(array_contenue):
    while(len(array_contenue)%16 != 0):
        array_contenue += "".ljust(1, "\x00")
    cipher_text = encryption.encrypt(array_contenue)
    return cipher_text

# Fonction qui arrete la lecture proprement 
def end_read(signal,frame):
    global continue_reading
    print ("Lecture terminee")
    continue_reading = False
    GPIO.cleanup()

signal.signal(signal.SIGINT, end_read)
MIFAREReader = MFRC522.MFRC522()

print ("Passer le tag RFID a lire")
array_contenue = ""

while continue_reading:
    
    # Detecter les tags
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # Une carte est detectee
    if status == MIFAREReader.MI_OK:
        print ("Carte detectee")
        
    
    # Recuperation UID
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    if status == MIFAREReader.MI_OK:
        print ("UID de la carte : "+str(uid[0])+"."+str(uid[1])+"."+str(uid[2])+"."+str(uid[3]))
    
        # Clee d authentification par defaut
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        # Selection du tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authentification
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        if status == MIFAREReader.MI_OK:
            array_contenue = MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
            continue_reading=False
        else:
            print ("Erreur d\'Authentification")
# on doit maintenant isoler le code contenu sur la carte
cipher_text = padding(array_contenue)
print(decryption(cipher_text))