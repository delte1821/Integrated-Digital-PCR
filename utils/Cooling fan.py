import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
DEBUG = 1
GPIO.setup(17, GPIO.OUT)

GPIO.output(17, False)
GPIO.cleanup()
    
