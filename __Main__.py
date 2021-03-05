# Module and documentation by Ji Wook Choi, BioNanoTechnologyLab(BNTL), Sogang University
#
# History:
# 2021-02-19 Created
# 2021-02-22 Updated FluImaging module
# 2021-02-23 Updated DigitalAnalysis module

# -----------------------------------------------------------------------------------------

# Import required packages
import bluetooth
import lightblue
import time
from datetime import datetime as dt
import os
from Modules.BT_Initializing import *
from Modules.ThermalCycling import *
from Modules.FluorescenceImaging import *
from Modules.DigitalAnalysis import *

# -----------------------------------------------------------------------------------------

# File directory
path       = os.getcwd()
SaveFolder = path + "/Savefiles"
date       = dt.now().strftime("%Y_%m_%d")
File_dir   = SaveFolder + "/" + date

# Make file directory & suffix
if not os.path.isdir(File_dir):
    os.mkdir(File_dir)
    print(File_dir)
suff = len(os.listdir(File_dir))

# -----------------------------------------------------------------------------------------

# Initializing bluetooth socket
BT_init()
print("Waiting for connection...")
server_socket=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
port = 1
server_socket.bind(("",port))
server_socket.listen(1)
client_socket,address = server_socket.accept()
print("Accepted connection from ",address)

db_file = "/home/pi/Desktop/IoT dPCR/Savefiles/IoT-dPCR.db"

# Initializing bluetooth communication variables
val    = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
buffer = ""
i      = 2
j      = 0

# -----------------------------------------------------------------------------------------

# Start module activation
while True:
    # Get data via bluetooth communication
    Serial = client_socket.recv(1024).decode('utf-8')
    print(Serial)
    Code   = Serial[0:2]
    print("Code: ", Code)
    
    # Convert data to array
    while (i < len(Serial)):
        if (Serial[i] != "_"):
            buffer += Serial[i]
            i      += 1
        else:
            val[j] = buffer
            buffer = ""
            j     += 1
            i     += 1
            
    # Initializing count variables
    i = 2
    j = 0
    
    # Thermalcyclling modules
    if(Code == "TC"):
        print("Thermalcycling activation")
        Temp1 = int(val[0])
        Temp2 = int(val[1])
        Temp3 = int(val[2])
        Time1 = int(val[3])
        Time2 = int(val[4])
        Time3 = int(val[5])
        Ncyc  = int(val[6])
        
        # Activate temperature profile
        dataname = WriteTprof(Ncyc, 10, 50, Time1, Temp1, Time2, Temp2, Time3, Temp3, SaveFolder)
        print(dataname) 
        
        '''
        # Print input variables
        print("Temp1 = ", Temp1)
        print("Temp2 = ", Temp2)
        print("Temp3 = ", Temp3)
        print("Time1 = ", Time1)
        print("Time2 = ", Time2)
        print("Time3 = ", Time3)
        print("Ncyc  = ", Ncyc)
        '''
        
    # Fluorescence imaing modules
    if(Code == "FI"):
        print("Fluimaging activation")
        ISO = int(val[0])
        ExpTime = int(val[1])
        ShuTime = int(val[2])
        LivTime = int(val[3])
        Flu = str(val[4])
        
        # Activate modules
        LiveImaging(ISO, ShuTime, LivTime)
        Img_dir = FluImaging(ISO, ShuTime, ExpTime, Flu, File_dir, dataname) # Get image directory
        
        '''
        # Print input variables
        print("ISO = ", ISO)
        print("ExpTime = ", ExpTime)
        print("ShuTime = ", ShuTime)
        print("LivTime = ", LivTime)
        print("Flu = ", Flu)
        '''        

    if(Code == "AN"):
        print("Analysis activation")
        Detparm1 = val[0]
        Detparm2 = val[1]
        Minrad = val[2]
        Maxrad = val[3]
        Mindist = val[4]
        
        # Activate modules
        DPCRanalysis(Detparm1, Detparm2, Minrad, Maxrad, Mindist, Img_dir, dataname)
        
        '''
        print("Detparm1 = ", Detparm1)
        print("Detparm2 = ", Detparm2)
        print("Minrad = ", Minrad)
        print("Maxrad = ", Maxrad)
        print("Mindist = ", Mindist)
        '''

# -----------------------------------------------------------------------------------------

client_socket.close()
server_socket.close()