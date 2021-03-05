# Importing required packages
import time
import picamera
import os
import RPi.GPIO as GPIO
import tkinter as tk
import sqlite3
import datetime
from scipy.signal import butter, lfilter, find_peaks 
import numpy as np
from numpy import convolve
import random
from fractions import Fraction

# Create function for measurment from ADC (8 channels 0 to 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    # Checking for correct channel
    if((adcnum > 7) or (adcnum < 0)):
        return -1
    GPIO.output(cspin,True)

    GPIO.output(clockpin, False)    # Start clock low
    GPIO.output(cspin,False)        # bring CS low

    commandout = adcnum
    commandout |= 0x11              # Check, startbit + single end bit
    commandout <<= 3                # Only sending 5 bits
    for i in range(5):
        if(commandout & 0x80):
            GPIO.output(mosipin,True)
        else:
            GPIO.output(mosipin,False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
    # read one empty bit, one null bit and 10 ADC bits
    for i in range(15):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if (GPIO.input(misopin)):
            adcout |= 0x1

    GPIO.output(cspin, True)

    adcout >>= 1            # First bit is null, so drop it
    adcout = adcout - 2*4095
    return adcout

# Function for converting ADC to voltage
def ADCtoV(ADC, Vref):
    
    '''
    # Definition of inputs:
    # ADC   - reading form MCP3304
    # Vref  - Reference voltage to MCP3304 [V]
    '''
    
    ADC = float(ADC)    # making sure ADC reading is a float\
    Voltage = ADC/4095 * Vref   # conversion to voltage
    return Voltage

def VtoT(Vin, Vsupp, R1, R2, R3, a, b):
    
    '''
    # Function converting voltage from a Wheatstone bridge to temperature measurement

    # Definition of inputs:
    # Vin   - Measured voltage of Wheatstone bridge [V]
    # Vsupp - Voltage supplied to Wheatstone bridge [V]
    # R1    - First resistance [Ohm]
    # R2    - Adjustable resistanc in parralel with measured resistance [Ohm]
    # R3    - Resistance in parallel with R1 [V]
    # a     - Factor for converting Resistance to T (T = (R-a)/b [Ohm]
    # b     - Factor for converting Resistance to T (T = (R-a)/b [Ohm/C]
    '''
    
    alpha = R2 / (R1 + R2) - Vin/Vsupp  # Factor alpha, see your notes
    Rmes = alpha * R1/(1 - alpha)               # Measured resistance
    T = (Rmes - a) / b                  # converting to temperature
        
    return T

# PID controller function
def PIDcont(Setpoint, MeasPoint,Kp,Ki,Kd,t,i0,e0):
    '''
    # PID controller function returns output value of PID controller (uPID), error of current itteration (e)
    # , and the current value of the integral for the Integral controller (I)

    # make sure function is called every t seconds

    # Definittion of inputs:
    # Setpoint = Desired value, here temperature
    # MeasPoint = Measured value, here temperature
    # Kp = Value for proptoional controller
    # Ki = Value for integral controller
    # Kd = Value for differential controller
    # t = Sampling time [s]
    # i0 = initial state of integrator (default =0)
    # e0 = Initial error (default = 0)
    '''
    
    # Initialisation
    k = 0                   # step variable
    Ii_prev = float(i0)     # Previous integration
    e_prev = float(e0)      # Previous error

    Kp = float(Kp)
    Ki = float(Ki)
    Kd = float(Kd)
    t = float(t)

    # Actual contoller  
    e = Setpoint - MeasPoint    # Callculating current error
    # Proportional:
    uP = Kp * e                 # Proportional part
    # Integral:
    I = Ii_prev + t * e         # Integral
    uI = Ki * I                 # Integral part
    Ii_prev = I                 # Updating integral for next interation
    # Differential
    dedt = (e - e_prev) / t     # Differential of error
    uD = Kd * dedt              # Differential part
    e_prev = e                  # Updating error
    # Overall controller output
    uPID = uP + uI + uD         # Overall PID output

    return (uPID,e,I)

# Function for movingaverage
def movingaverage(values,window):
    weights = np.repeat(1.0,window)/window
    sma = np.convolve(values,weights,'valid')
    return sma

# Thermal cycling
def WriteTprof(Ncyc,tHS,Ths,tDE,Tde,tAN,Tan,tEX,Tex, File_dir):
    
    # Initialsing
    GPIO.setmode(GPIO.BCM)
    DEBUG = 1
    
    # SQL operations
    dbname = File_dir + "/" + 'IoT-dPCR.db'
    conn = sqlite3.connect(dbname)    # Connecting to database
    c = conn.cursor()                           # Creating cursor for access
    # Creating table with experiments index (if it does not exist)
    c.execute('CREATE TABLE IF NOT EXISTS experiments (Date varchar(255), Dataname varchar(255))')


    # Creating table in SQL database to save data to
    date = datetime.date.today()                # Determining current data
    rows = c.execute('''select * from experiments''')   # Finding previous number of experiments
    rows = rows.fetchall()
    rows = len(rows)+1                          # Incrementing by one to create new unique index
    dataname = 'data_'+str(rows)                # Unique name for table containging cycling data
    c.execute('Insert INTO experiments (Date, Dataname) VALUES (?,?)',(date,dataname))  # Adding thermal data table to db
    conn.commit()                               # Comminting change to db

    # Creating table for Experimental data
    c.execute('CREATE TABLE IF NOT EXISTS ' + dataname + ' (Time, ADC, Volt, MeasT, SetT, PID, PWM, Temp)')
    
    # Defining parameters
    variables = c.execute('SELECT Valuenumber FROM Variables')
    variables = [float(item[0]) for item in variables.fetchall()]
   
    # Variables as imported from database
    Freq = variables[0]     # Number of measurements per second [Hz]
    Vref = variables[1]     # Reference voltage from ADC [V]
    Vsupp = variables[2]    # Voltage supplied to wheatsonte bridge [V]
    R1 = variables[3]       # Resistance for wheatstone bridge [Ohm]
    R2 = variables[4]       # Adjustable resistance for Wheatstone bridge [Ohm]
    R3 = variables[5]       # Resistance for wheatstone bridge [Ohm]
    a = variables[6]        # Factor for resistance to temperature conversion [Ohm]
    b = variables[7]        # Factor for resistance to temperature conversion [Ohm/C]
    Kp = variables[8]       # Value for K part
    Ki = variables[9]       # Value for I part
    Kd = variables[10]      # Value for d part
    fc = variables[11]      # Cut of frequency in Hz for low pass filter
    freq_PWM = variables[12]# Frequency for PWM in Hz
    maxPID = variables[13]  # Value for conversion of PID to PWM
    fan_threshold = variables[14] # threshold for PID value, below which fan will turn on
    
    # Initialising parameters for cycling
    e = 0       # Inital error
    I = 0       # Inital integral
    j = 0           # Counter for cycles
    i = 0           # Counter for steps
    intTime = 0     # Internal timer for step times
    setTime = 0     # Target time for step
    TotTime = 0
    Time1 = 0       # Overall elappsed time
    fanon = 0       # is the cooling fan on? 0 for no, 1 for yes
    dcycle_PWM = 50 # Default duty cycle for PWM in %
    fs = float(Freq)    # Sampling frequency for low pass filter
    w = fc / (fs / 2)   # Normalize the frequency for low pass filter

    # Making sure everything is a float
    Vref= float(Vref)
    Vsupp= float(Vsupp)
    R1 = float(R1)
    R2 = float(R2)
    R3 = float(R3)
    a = float(a)
    b = float(b)
    Freq = float(Freq)

    # Defingin pin connections
    SPICLK = 18     # For ADC
    SPIMISO = 23    # For ADC
    SPIMOSI = 24    # For ADC
    SPICS = 25      # For ADC
    PINPWM = 27     # Pin for PWM
    PINFAN = 17     # Pin for active cooling with fan

    # Define Pin connection to ADC 3008
    potentiometer_adc = 1 #Ch2
   
    # Setup SPI interface pins
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)
    GPIO.setup(PINPWM, GPIO.OUT)
    GPIO.setup(PINFAN, GPIO.OUT)
    
    # Calculating number of measurments and waitung time
    Waitt = 1/Freq # Waiting time between two measurments [s]

    # Setting up PWM
    func_PWM = GPIO.PWM(PINPWM, freq_PWM)

    # Measurment loop   
    func_PWM.start(0) # Starting PWM
    while j <= Ncyc:     
        if (j == 0 & i != 66.6): # Hot start, random number so true for all i, if j = 0
            setT = Ths
            setTime = tHS
            i = 2 # So once timer is up this gets updated to cycling
        elif (j >= 0 and i == 0):     # Cycling: Denaturation
            setT = Tde
            setTime = tDE
        elif (j >= 0 and i == 1):     # Cycling: Annealing
            setT = Tan
            setTime = tAN
        elif (j >= 0 and i == 2):     # Cycling: Extension
            setT = Tex
            setTime = tEX
        
        # Reading ADC value
        trim_pot = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS) # Ch1
        # Converting to voltage
        voltage = ADCtoV(trim_pot,Vref)
        # Converting to temperature
        Temperature = VtoT(voltage, Vsupp, R1, R2, R3, a, b)
                
        # Determining time
        Time1 = Time1 + Waitt
        Time1 = round(Time1, 1)
        # Using PID
        (uPID,e,I) = PIDcont(setT, Temperature,Kp,Ki,Kd,Waitt,e,I)  # PIDcont(Setpoint, MeasPoint,Kp,Ki,Kd,t,i0,e0)

        # Determining new Duty cycle to achieve heating / cooling
        dcycle_PWM = uPID / maxPID # Calculating new dutycycle according to PID
        # Making sure new Duty cycle is maximum 100% and minimum 0
        if dcycle_PWM > 100:
            dcycle_PWM = 100
        elif dcycle_PWM < 0:
            dcycle_PWM = 0
        #print(uPID)
        # Leave Space here for cooling fan if required
        # Turn Fan on if PID << 0
        # Turn off if PID > 0
        if (uPID <= fan_threshold) and (fanon == 0): # turn on fan
            fanoon = 1
            GPIO.output(PINFAN,True)

        else:  # turn off fan
            fanoon = 0
            GPIO.output(PINFAN,False)
          

        # Updating Duty Cycle
        func_PWM.ChangeDutyCycle(dcycle_PWM)
            
        # Writing data to database
        c.execute('INSERT INTO ' +dataname + ' VALUES ('+ str(Time1) +',' + str(trim_pot) +', ' + str(voltage) + ', ' + str(Temperature) + ', ' + str(setT) + ', ' + str(uPID) + ', ' + str(dcycle_PWM) + ', 0)')
              
        time.sleep(Waitt)

        # Updating timers and moving to next step / cycle if required
        intTime = intTime + Waitt

        if intTime >= setTime:  # Time for step ellapsed
            i = i+1             # Moving on to next step
            intTime = 0         # Reseting time
            if i >= 3:          # Moving to next cycle
                i = 0           # Reseting step counter
                j = j+1         # Moving to next cycle
                e = 0           # Reseting error for PID
                I = 0           # Reseting integral for PID
        
        
            
        
    # Clearing GPIOs and stopping LEDs
    func_PWM.stop() # Stoping PWM
    GPIO.cleanup()

    # Callculating filtered Temperature
    # Retriving Temperature Data
    conn.commit()
    Temp = c.execute('Select MeasT from ' + dataname)   # Getting data from db
    Temp = [item[0] for item in Temp.fetchall()]        # Removing touples

    # Filtering
    b, a = butter(1,w, 'low')                           # Designing Filter
    Tempfill = lfilter(b,a,Temp)                          # Filtering data
    Tempfill = movingaverage(Tempfill,4)

    # Adding data to db
    for i in range(0,len(Tempfill)):
        c.execute('UPDATE '+dataname+' SET Temp = ? WHERE MeasT = ?',(Tempfill[i]+0.45,Temp[i]))   # Updating last collumn
    conn.commit()                                                                   # Commiting changes
    
    conn.close()
    print('Run Complete')
    return dataname

if __name__ == '__main__':
    # WriteTprof(Ncyc,tHS,Ths,tDE,Tde,tAN,Tan,tEX,Tex, File_dir)
    WriteTprof(1, 1, 10, 1, 20, 1, 30, 1, 40, '/home/pi/Desktop/IoT dPCR/Savefiles')
