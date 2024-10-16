#!/usr/bin/python3

import os
import signal
import threading
from time import sleep

import serial
import bluetooth


def set_rfcomm_server():
    """Set BT rfcomm server socket"""
    global server_sock
    server_sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
    port = 1
    server_sock.bind(("",port))
    server_sock.listen(1)

def set_rfcomm_client():
    """Set BT rfcomm client socket"""
    global client_sock
    client_sock, addr = server_sock.accept()
    print("Accepted connection from ", addr)

def handler(signum, frame):
    """Set exitthread signal handler"""
    global exitthread
    exitthread = True
    print("exitthread executed")

#Main thread
def nmea_send(GPSdata):
    
    global disconnected

    #Make list of data line
    serdata = []

    while exitthread == False:

        #Client disconnected state
        if disconnected == True:
            set_rfcomm_client()
            #Go to client connected state
            disconnected = False

        #Client connected state
        if disconnected == False:
            for c in GPSdata.read():
                serdata.append(chr(c))
            
                #Process if one line of serial data appended
                if c == 10: #/n

                    #When client connected
                    try:
                        #Join appended serial data to NMEA line data
                        NMEA_line = ''.join(serdata)

                        #Send NMEA line data to rfcomm client socket
                        client_sock.send(NMEA_line)

                        #delete appended serial data
                        del serdata[:]

                    #When client disconnected
                    except OSError:
                        #delete appended serial data
                        del serdata[:]
                        #Go to client disconnected state
                        disconnected = True

"""Set GPS serial port"""
uart = serial.Serial(port = '/dev/ttyS0', baudrate = 115200, timeout=0.1)

if __name__ == '__main__':

    os.system('sudo sdptool add sp')

    #Set BT sockets
    set_rfcomm_server()
    set_rfcomm_client()

    #Set initial state
    exitthread = False
    disconnected = False

    #Set exit thread signal (Ctrl+C)
    signal.signal(signal.SIGINT, handler)

    #Set NMEA send thread and start
    nmea_send_thread = threading.Thread(target=nmea_send, args=(uart,))
    nmea_send_thread.start()


    #Terminate code (for develop test)
    while 1:

        sleep(0.1)

        if exitthread == False:
            break
        if exitthread == True:
            client_sock.close()
            server_sock.close()