
import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import Adafruit_CharLCD as LCD

from Crypto.Cipher import AES
import os
import struct
import sys

import sqlite3

from pad4pi import rpi_gpio

# Fonction de decryption

def decryption(cipher_text):
# decryption
    key_file = open("base_key.key", "r")
    key = key_file.read()
    decryption = AES.new(key[:32], AES.MODE_CBC, 'This is an IV456')
    decrypt_text = decryption.decrypt(cipher_text)
# j'enleve le padding
    i = 0
    for c in decrypt_text:
        if(c=='\''):
            number = i
            break
        i += 1
    plain_text=decrypt_text[0:i].decode('utf-8')
    return plain_text

# padding du plain_text pour qu'il ait une taille multiple de 16 byte

def padding(array_contenue):
    print(array_contenue)
    convert = ''
    for dec in array_contenue:
        convert += chr(dec) 
    while(len(convert)%16 != 0):
        convert += "".ljust(1, "\x00")
    return convert

# Fonction qui arrete la lecture proprement 
def end_read(signal,frame):
    global continue_reading
    print ("Lecture terminee")
    continue_reading = False
    GPIO.cleanup()

# fonction qui connecte la db et retourne le curseur
def connect_db():
    connection = sqlite3.connect('db.db')
    cursor = connection.cursor() 
    return connection, cursor

# permet d'affcher la touche 

def printKey(key):
  global mdp_input
  mdp_input += key
  
# Setup Keypad
KEYPAD = [
        ["1","2","3"],
        ["4","5","6"],
        ["7","8","9"],
        ["*","0","#"]
]

# same as calling: factory.create_4_by_4_keypad, still we put here fyi:
ROW_PINS = [5, 6, 13, 19] # BCM numbering
COL_PINS = [16, 20, 21] # BCM numbering

factory = rpi_gpio.KeypadFactory()

# Try factory.create_4_by_3_keypad
# and factory.create_4_by_4_keypad for reasonable defaults
keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)
keypad.registerKeyPressHandler(printKey)

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

while(True):
    
    mdp_input = ""
    
    signal.signal(signal.SIGINT, end_read)
    MIFAREReader = MFRC522.MFRC522()
    print ("Passer le tag RFID a lire")
    array_contenue = ""
    continue_reading = True
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
    plain_text = decryption(cipher_text)
    id = plain_text[:4]
    id = int(id)
    i = 0
    for c in plain_text[4:]:
        if c=="0" or c=="1" or c=="2" or c=="3" or c=="4" or c=="5" or c=="6" or c=="7" or c=="8" or c=="9": 
            break
        else:
            i+=1
    password = plain_text[i+4:i+8]
    password = int(password)

    # on va chercher le mdp de la carte dans la base de donee
    connection, cursor = connect_db()
    cursor.execute("SELECT Password FROM User WHERE ID = ?", (id,))
    password_db = cursor.fetchone()[0]

    # on demande a l'utilisateur de rentrer son mdp et on compare les deux
    lcd.clear()
    lcd.message("Code :")
    mdp_input=""
    while(len(mdp_input)!=4):
        time.sleep(0.2)
        if len(mdp_input)==1:
            lcd.clear()
            lcd.message("Code : *")
        if len(mdp_input)==2:
            lcd.clear()
            lcd.message("Code : **")
        if len(mdp_input)==3:
            lcd.clear()
            lcd.message("Code : ***")
        if len(mdp_input)==4:
            lcd.clear()
            lcd.message("Code : ****")
            time.sleep(1)
    lcd.clear()
    access = "Empty"
    if int(mdp_input)==password:
        lcd.message("Sucess")
        access = "Full"
    else:
        lcd.message("Fail")
    time.sleep(2)
    lcd.clear()

    # on cherche quelle casier ouvrir selon leurs contenue
    if access=="Full":
        cursor.execute("SELECT Number FROM Locker WHERE State = ?", (access,))
        number = cursor.fetchone()
        if number==None:
            lcd.clear()
            lcd.message("Casier vide")
            time.sleep(3)
        else:
            message = "Casier "+str(number[0])+" ouvert"
            lcd.clear()
            lcd.message(message)
            time.sleep(3)
            cursor.execute("UPDATE Locker SET State = 'Empty' WHERE Number = ?", (number[0],))
        connection.commit()
        connection.close()
    lcd.clear()
    MIFAREReader.MFRC522_Reset()