import serial
import signal
import threading

#Set exitthread signal handler
def handler(signum, frame):
    global exitthread
    exitthread = True
    print("exitThread executed")

#Main thread
def nmea_read(GPSdata):
    
    #Make list of data line
    serdata = []

    while exitthread == False:
        for c in GPSdata.read():
            serdata.append(chr(c))
            
            #Process if one line of serial data appended
            if c == 10: #/n

                #Join appended serial data to NMEA line data
                NMEA_line = ''.join(serdata)

                print(NMEA_line)

                #delete appended serial data
                del serdata[:]


#Set serial port
uart = serial.Serial(port = '/dev/ttyS0', baudrate = 115200, timeout=0.1)

if __name__ == '__main__':

    #Set initial state
    exitthread = False

    #Set exit thread signal (Ctrl+C)
    signal.signal(signal.SIGINT, handler)

    #Set NMEA read thread and start
    nmea_read_thread = threading.Thread(target=nmea_read, args=(uart,))
    nmea_read_thread.start()

    #Terminate code (for develop test)
    while 1:
        if exitthread == False:
            break
        if exitthread == True:
            nmea_read_thread.raise_exception()