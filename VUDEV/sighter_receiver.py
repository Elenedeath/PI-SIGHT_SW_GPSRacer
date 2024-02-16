#!/usr/bin/python3

import os
import threading

import serial
import bluetooth

def _init_():
  os.system('sudo sdptool add sp')

  global exitthread
  exitthread = False

  global connected
  connected = True

  global nowspeed_kph_rounded
  nowspeed_kph_rounded = 0

  global bestspeed_kph_rounded
  bestspeed_kph_rounded = 0

def set_rfcomm_server():
  """Set BT rfcomm server socket"""
  global server_sock
  server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
  port = 1
  server_sock.bind(("",port))
  server_sock.listen(1)

def set_rfcomm_client():
  """Set BT rfcomm client socket"""
  global client_sock
  client_sock, addr = server_sock.accept()
  print("Accepted connection from ", addr)

def data_process(GPSdata):
  """GPS data process"""

  global connected
  serdata = []
  nmea_buff = 0
  nowspeed = []
  global nowspeed_kph_rounded
    
  while exitthread == False:

    #Client connected state
    if connected == True:
      for c in GPSdata.read():
        serdata.append(chr(c))
          
        #Process if one line of serial data appended
        if c == 10: #/n

          #When client connected
          try:
            nmea_line = ''.join(serdata)
            client_sock.send(nmea_line)
            serdata.clear()

            #Find GNRMC and update nowspeed and bestspeed
            received_data = (str)(nmea_line) 
            gnrmc_info = "GNRMC"
            GNRMC_data_available = received_data.find(gnrmc_info)
            if (GNRMC_data_available>0):
              GNRMC_buffer = received_data.split("$GNRMC,",1)[1]
              nmea_buff = (GNRMC_buffer.split(','))
              nowspeed = nmea_buff[6]
              nowspeed_kph = float(nowspeed)*1.852
              nowspeed_kph_rounded = round(float(nowspeed_kph),1)

              if exitthread == True:
                break

          #When client disconnected
          except OSError:
            serdata.clear()
            nowspeed_kph_rounded = 0
            #Go to client disconnected state
            connected = False

    #Client disconnected state
    if connected == False:
      #set_rfcomm_client()
      #connected = True
      break

  client_sock.close()
  server_sock.close()
  print("Sockets closed")

def get_nowspeed_kph():
  return nowspeed_kph_rounded

def get_bestspeed_kph():
  global bestspeed_kph_rounded
  if bestspeed_kph_rounded < nowspeed_kph_rounded :
    bestspeed_kph_rounded = nowspeed_kph_rounded
  return bestspeed_kph_rounded

def main():

  _init_()

  set_rfcomm_server()
  set_rfcomm_client()

  uart = serial.Serial(port = '/dev/ttyS0', baudrate = 115200, timeout=0.1)

  data_process_thread = threading.Thread(target=data_process, args=(uart,))
  data_process_thread.start()

def termination():
  global exitthread
  exitthread = True
  print("exitthread executed")


if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    termination()