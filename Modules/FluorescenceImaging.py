# -----------------------------------------------------------------------------------------

# Import required packages
import time
import picamera
import os
import RPi.GPIO as GPIO
import sqlite3
import datetime
import numpy as np
from numpy import convolve
import random
from fractions import Fraction
import cv2
import math
from PIL import ImageTk, Image
from datetime import datetime as dt

# -----------------------------------------------------------------------------------------

'''
Camera setting parameters

    camera.rotation = 90
    camera.resolution = (3280,2464)
    camera.awb_mode = 'fluorescent'
    camera.awb_gains = (0.5, 0.5)
    camera.exposure_mode = "night"
    camera.sensor_mode = 2
    camera.raw_format = 'rgb'
'''

# -----------------------------------------------------------------------------------------

#from utils import Crop_G2, Crop_R2
def LiveImaging(ISO, SHU, tLive):
    
    #Initialization
    camera= picamera.PiCamera()

    # GPIO setting
    PINR = 21  # PIN number setting
    PING = 20
    GPIO.setmode(GPIO.BCM)    # Use board pin numbering
    GPIO.setup(PINR,GPIO.OUT)      # Define pin seven as out
    GPIO.setup(PING,GPIO.OUT)      # Define pin seven as out
    
   
    # Camera setting
    camera.iso = ISO
    camera.shutter_speed = SHU * 1000

    # Start live imaging
    GPIO.output(PING,True)         # Turn on pin
    GPIO.output(PINR,True)         # Turn on pin
    camera.start_preview()
    time.sleep(tLive)
    camera.stop_preview()
    GPIO.output(PING,False)         # Turn on pin
    GPIO.output(PINR,False)         # Turn on pin
    
    camera.close()
    GPIO.cleanup()
    
    return

# -----------------------------------------------------------------------------------------

def FluImaging(ISO, tSHU, tEXP, Flu, File_dir, ID):
    
    # Make file directory & IDix
    date       = dt.now().strftime("%Y_%m_%d")
    Img_dir   = File_dir + "/Images" + "/" + date
    tag = ".jpeg"
    
    if not os.path.isdir(Img_dir):
        os.mkdir(Img_dir)
        print(Img_dir)
    
    #Initialization
    camera= picamera.PiCamera()
    
    # Determine LED pin & file name
    if (Flu == "G"):
        PINLED = 20
        Img_name = Img_dir + "/" + ID + "_G"
        print(Img_name)
    elif (Flu == "R"):
        PINLED = 21
        Img_name  = Img_dir + "/" + ID + "_R"
    elif (Flu == "Y"):
        PINLED = 19
        Img_name  = Img_dir + "/" + ID + "_Y"
    else:
        print("Error: FluType")

    # GPIO initializing
    GPIO.setmode(GPIO.BCM)           # Use board pin numbering
    GPIO.setup(PINLED,GPIO.OUT)      # Define pin as out
    
    # Camera setting
    camera.awb_mode = 'fluorescent'
    camera.awb_gains = (0.5, 0.5)
    camera.exposure_mode = "night"
    camera.sensor_mode = 2
    camera.raw_format = 'rgb'
    camera.iso = ISO
    camera.shutter_speed = tSHU * 1000
    camera.resolution = (1920,1080)
    
    # Taking fluorescence images
    GPIO.output(PINLED,True)         # Turn on pin
    camera.start_preview()           # Start preview
    time.sleep(tEXP)                 # Exposure LED
    camera.stop_preview()            # Stop preview
    camera.capture(Img_name + tag)         # Image taking
    GPIO.output(PINLED,False)        # Turn off pin
    
    # Crop image
    CropImg(Img_name)
    
    camera.close()
    GPIO.cleanup()
       
    return Img_dir

# -----------------------------------------------------------------------------------------

def CropImg(Img_Name):
    tag = ".jpeg"
    # Read image
    img = cv2.imread(Img_Name + tag)
    
    # Crop image
    Crimg1 = img[0:300, 420:1300] #[y:y+h, x:x+w]
    Crimg2 = img[350:650, 420:1300] #[y:y+h, x:x+w]
    Crimg3 = img[700:1000, 420:1300] #[y:y+h, x:x+w]
    
    # Save images
    Crimg_name1 = Img_Name + "_1" + tag
    Crimg_name2 = Img_Name + "_2" + tag
    Crimg_name3 = Img_Name + "_3" + tag
    
    cv2.imwrite(Crimg_name1, Crimg1)
    cv2.imwrite(Crimg_name2, Crimg2)
    cv2.imwrite(Crimg_name3, Crimg3)

if __name__ == '__main__':
    #LiveImaging(1600, 6000, 30)
    FluImaging(1600, 6000, 3, 'G',"/home/pi/Desktop/IoT-dPCR/Savefiles", 'test1')