import os

def BT_init():
    os.system('sudo hciconfig hci0 up \n')
    os.system('sudo hciconfig hci0 piscan \n')
    os.system('sudo sdptool add --channel=1 SP \n')
    #os.system('sudo rfcomm listen 0 1& \n')

if __name__ == '__main__':
    BT_init()