
import RPi.GPIO as GPIO
import MFRC522
import signal

import time
import Adafruit_CharLCD as LCD

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

# Fonction qui arrete la lecture proprement 
def end_read(signal,frame):
    global continue_reading
    print ("Lecture terminée")
    continue_reading = False
    GPIO.cleanup()

signal.signal(signal.SIGINT, end_read)
MIFAREReader = MFRC522.MFRC522()

print ("Passer le tag RFID a lire")

while continue_reading:
    
    # Detecter les tags
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # Une carte est detectee
    if status == MIFAREReader.MI_OK:
        print ("Carte detectee")
        lcd.message('Carte detectee')
    
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
            MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
        else:
            print ("Erreur d\'Authentification")
