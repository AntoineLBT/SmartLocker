import RPi.GPIO as GPIO
import time

# fonction registre 
def clean_register(nombre_pin):
    for i in range(0, nombre_pin):
        registre[0] = 0

def setup_register(index, value):
    registre[index] = value

def write_register(nombre_pin):
    GPIO.output(RCLK_Pin, GPIO.LOW)
    for i in range(0, nombre_pin):
        GPIO.output(SRCLK_Pin, GPIO.LOW)
        val = registre[i]
        if val == 1:
            GPIO.output(SER_Pin, GPIO.HIGH)
            print("on")
        else:
            GPIO.output(SER_Pin, GPIO.LOW)
        GPIO.output(SRCLK_Pin, GPIO.HIGH)
    GPIO.output(RCLK_Pin, GPIO.HIGH)
    GPIO.output(SRCLK_Pin, GPIO.LOW)
    

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
registre = [0, 0, 0, 0, 0, 0, 0, 0]
nombre_pin = 8
SER_Pin = 2
RCLK_Pin = 3
SRCLK_Pin = 4
GPIO.setup(SER_Pin, GPIO.OUT)
GPIO.setup(RCLK_Pin, GPIO.OUT)
GPIO.setup(SRCLK_Pin, GPIO.OUT)

setup_register(0, 1)
setup_register(1, 0)
setup_register(2, 1)
write_register(nombre_pin)