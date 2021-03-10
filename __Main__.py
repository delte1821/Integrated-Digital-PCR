# Module and documentation by Ji Wook Choi, BioNanoTechnologyLab(BNTL), Sogang University

# History:
# 2021-02-19 Created
# 2021-02-22 Updated FluImaging module
# 2021-02-23 Updated DigitalAnalysis module
# 2021-03-05 Git update
# 2021-03-06 GPS information update
# 2021-03-08 Fluorescence imaging & analysis updates
# 2021-03-10 Initializing file added

# -----------------------------------------------------------------------------------------

# Import required packages
import bluetooth
import time
from datetime import datetime as dt
import os
import sqlite3
from __init__ import *
from Modules.ThermalCycling import *
from Modules.FluorescenceImaging import *
from Modules.DigitalAnalysis import *

# -----------------------------------------------------------------------------------------
# Initializing
SaveFolder, date = FD_init() # File directory initializing
client_socket,address = BT_init() # Bluetooth initializing
db_dir = DB_init() # Database initializing

# Initializing bluetooth communication variables
val    = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
buffer = ""
i      = 0
j      = 0

# -----------------------------------------------------------------------------------------
# Start module activation
while True:
    # Get data via bluetooth communication
    Serial = client_socket.recv(1024).decode('utf-8')
    print(Serial)
    
    # Convert serial data to list
    while (i < len(Serial)):
        if (Serial[i] != "_"):
            buffer += Serial[i]
            if (buffer == '\r' or buffer =='\n'):
                buffer = ""
            i += 1
        else:
            val[j] = buffer
            buffer = ""
            j     += 1
            i     += 1
            
    # Update count variables
    i = 0
    j = 0
    Code = val[0]
    print("Code: ", Code)
    
    # Thermalcyclling modules
    if(Code == "TC"):
        print("Thermalcycling activation")
        Temp1 = int(val[1])
        Temp2 = int(val[2])
        Temp3 = int(val[3])
        Time1 = int(val[4])
        Time2 = int(val[5])
        Time3 = int(val[6])
        Ncyc  = int(val[7])
        ID    = str(val[8])
        
        # Activate temperature profile
        dataname = WriteTprof(Ncyc, 10, 50, Time1, Temp1, Time2, Temp2, Time3, Temp3, SaveFolder, ID)
         
        '''
        # Print input variables
        print(dataname)
        print("Temp1 = ", Temp1)
        print("Temp2 = ", Temp2)
        print("Temp3 = ", Temp3)
        print("Time1 = ", Time1)
        print("Time2 = ", Time2)
        print("Time3 = ", Time3)
        print("Ncyc  = ", Ncyc)
        '''
        
        # Update variables
        val    = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        Code = val[0]
        
    # Fluorescence imaing modules
    elif(Code == "FI"):
        print("Fluimaging activation")
        ISO     = int(val[1])
        ExpTime = int(val[2])
        ShuTime = int(val[3])
        LivTime = int(val[4])
        Flu     = str(val[5])
        ID      = str(val[6])
        
        # Activate modules
        LiveImaging(ISO, ShuTime, LivTime)
        Img_dir = FluImaging(ISO, ShuTime, ExpTime, Flu, SaveFolder, ID) # Get image directory
        
        '''
        # Print input variables
        print("ISO = ", ISO)
        print("ExpTime = ", ExpTime)
        print("ShuTime = ", ShuTime)
        print("LivTime = ", LivTime)
        print("Flu = ", Flu)
        '''
        # Update variables
        val    = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        Code = val[0]

    elif(Code == "AN"):
        print("Analysis activation")
        Detparm1 = val[1]
        Detparm2 = val[2]
        Minrad   = val[3]
        Maxrad   = val[4]
        Mindist  = val[5]
        ID       = val[6]
        
        # Activate modules
        Conc = Imganalysis(Detparm1, Detparm2, Minrad, Maxrad, Mindist, Img_dir, dataname, ID)
        
        '''
        # Print input variables
        print("Detparm1 = ", Detparm1)
        print("Detparm2 = ", Detparm2)
        print("Minrad = ", Minrad)
        print("Maxrad = ", Maxrad)
        print("Mindist = ", Mindist)
        '''
        
        # Update variables
        val    = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        Code = val[0]
        
    elif(Code == "ID"):
        print("Client information")
        # Get GPS information from smartphone
        ID = val[1]
        Longitude = val[3]
        Latitude = val[4]
        Altitude = val[5]
        Serverid = val[6]
        
        # Write GPS information to database file
        conn = sqlite3.connect(db_dir)
        c = conn.cursor()
        c.execute('''INSERT INTO Client VALUES (?, ?, ?, ?)''', (str(ID) ,str(Longitude) ,str(Latitude) ,str(Altitude))) 
        conn.commit()
        conn.close()
        
        '''
        # Print input variables
        print("ID: ", ID)
        print("Longitude: ", Longitude)
        print("Latitude: ", Latitude)
        print("Altitude: ", Altitude)
        print("Server id: ", Serverid)
        '''
        
        # Update variables
        val    = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        Code = val[0]

# -----------------------------------------------------------------------------------------
client_socket.close()
server_socket.close()
conn.commit()
conn.close()