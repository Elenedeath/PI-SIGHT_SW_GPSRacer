import serial               #import serial pacakge
import sys                  #import system package
import time

#convert raw NMEA string into degree decimal format   
def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.4f" %(position)
    return position

def GPS_Info():
    global NMEA_buff
    global lat_in_degrees
    global long_in_degrees
    nmea_time = []
    nmea_latitude = []
    nmea_longitude = []
    nmea_time = NMEA_buff[0]                    #extract time from GNRMC string
    nmea_latitude = NMEA_buff[2]                #extract latitude from GNRMC string
    nmea_longitude = NMEA_buff[4]               #extract longitude from GNRMC string
    nmea_speed = NMEA_buff[6]                   #extract speed over ground from GNRMC string

    lat = float(nmea_latitude)                  #convert string into float for calculation
    longi = float(nmea_longitude)               #convertr string into float for calculation
    
    lat_in_degrees = convert_to_degrees(lat)    #get latitude in degree decimal format
    long_in_degrees = convert_to_degrees(longi) #get longitude in degree decimal format 

    time_KST = float(nmea_time)+90000
    speed_kph = float(nmea_speed)*1.852

    print("NMEA Time: ", nmea_time,'\n')
    print("NMEA Latitude:", nmea_latitude,"NMEA Longitude:", nmea_longitude,'\n')
    print("time in KST(UTC+9):", int('%06i' % time_KST),'\n')
    print("lat in degrees:", lat_in_degrees," long in degree: ", long_in_degrees, '\n')
    print("speed over ground: ", round(float(speed_kph),1),"kph",'\n')
    print("------------------------------------------------------------\n")


ser = serial.Serial(port = '/dev/ttyS0', baudrate = 115200, timeout=0.1)              #Open port with baud rate

GNRMC_buffer = 0
NMEA_buff = 0
lat_in_degrees = 0
long_in_degrees = 0

try:
    while True:
        received_data = (str)(ser.readline())                   #read NMEA string received
        gnrmc_info = "$GNRMC,"
        GNRMC_data_available = received_data.find(gnrmc_info)   #check for NMEA GNRMC string                 
        
        if (GNRMC_data_available>0):
            GNRMC_buffer = received_data.split("$GNRMC,",1)[1]  #store data coming after "$GNRMC," string 
            NMEA_buff = (GNRMC_buffer.split(','))               #store comma separated data in buffer
            GPS_Info()                                          #get time, latitude, longitude
        
        if (GNRMC_data_available==0):
            time.sleep(0.1)
            break

except KeyboardInterrupt:
    sys.exit(0)