#!/usr/bin/env python
# -*- coding: utf8 -*-
# Version modifiee de la librairie https://github.com/mxgxw/MFRC522-python

import RPi.GPIO as GPIO
import MFRC522
import signal
from encryption import encryption, decryption

import sqlite3
continue_reading = True

# Fonction qui arrete la lecture proprement 
def end_read(signal,frame):
    global continue_reading
    print ("Lecture terminée")
    continue_reading = False
    GPIO.cleanup()

def connect_db():
    connection = sqlite3.connect('../RFID/db.db')
    cursor = connection.cursor() 
    return connection, cursor

signal.signal(signal.SIGINT, end_read)
MIFAREReader = MFRC522.MFRC522()

data = []
# creation dun profile dans la db
connect, cursor = connect_db()
texte = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
mdp = ''
while(len(texte) > 8):
    texte = raw_input("Entrez le nom ou initiale de 8 caractère max:\n")
while(len(mdp)!=4):
    mdp = raw_input("Entrez un code pin de 4 caractère maximum:\n")
user_data = texte+mdp
cursor.execute("INSERT INTO User (Name, Password, State) VALUES (?, ?, 'User')",(texte, mdp,))
connect.commit()
cursor.execute("SELECT ID FROM User WHERE Name=?", (texte,))
id = cursor.fetchone()[0]
if id < 10:
    data_to_card = "000" + str(id) + user_data
elif id < 100:
    data_to_card = "00" + str(id) + user_data
elif id < 1000: 
    data_to_card = "0" + str(id) + user_data
else:
    data_to_card = str(id) + user_data

print("data_to_card :", data_to_card)
data_to_card = encryption(data_to_card)
for c in data_to_card:
    if (len(data)<16):
        data.append(int(ord(c)))
while(len(data)!=16):
    data.append(0)
print(data)
print ("Placez votre carte RFID")

while continue_reading:
      
    # Detecter les tags
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # Une carte est detectee
    if status == MIFAREReader.MI_OK:
        print ("Carte detectee")
    
    # Recuperation UID
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    if status == MIFAREReader.MI_OK:

        # Print UID
        print ("UID de la carte : "+str(uid[0])+"."+str(uid[1])+"."+str(uid[2])+"."+str(uid[3]))
    
        # Clee d authentification par defaut
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        # Selection du tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authentification
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        if status == MIFAREReader.MI_OK:
            print ("Le secteur 8 contient actuellement : ")
            MIFAREReader.MFRC522_Read(8)

            print ("Ecriture ...")
            MIFAREReader.MFRC522_Write(8, data)

            print ("Le secteur 8 contient maintenant : ")
            MIFAREReader.MFRC522_Read(8)

            # Stop
            MIFAREReader.MFRC522_StopCrypto1()
            continue_reading = False

        else:
            print ("Erreur d authentication")
