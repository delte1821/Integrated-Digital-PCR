import os
import bluetooth
import sqlite3
from datetime import datetime as dt

def FD_init():
    path       = os.getcwd()
    SaveFolder = path + "/Savefiles"
    date       = dt.now().strftime("%Y_%m_%d")
    return SaveFolder, date

def BT_init():
    os.system('sudo hciconfig hci0 up \n')
    os.system('sudo hciconfig hci0 piscan \n')
    os.system('sudo sdptool add --channel=1 SP \n')
    #os.system('sudo rfcomm listen 0 1& \n')
    
    print("Waiting for connection...")
    server_socket=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    port = 1
    server_socket.bind(("",port))
    server_socket.listen(1)
    client_socket,address = server_socket.accept()
    print("Accepted connection from ",address)
    
    return client_socket,address

def DB_init():
    db_dir = "/home/pi/Desktop/IoT-dPCR/Savefiles/IoT-dPCR.db"
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS Client')
    c.execute('CREATE TABLE IF NOT EXISTS Client (ID, Longitude, Latitude, Altitude)')
    conn.commit()
    conn.close()
    
    return db_dir
    
if __name__ == '__main__':
    BT_init()