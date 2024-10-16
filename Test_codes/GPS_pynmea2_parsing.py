#!/usr/bin/python3

import io
import time
import logging
import sys
import os

import pytz
import pynmea2
import serial
from timezonefinder import TimezoneFinder

def wait_active_set_time():
    """Wait until active state and set Timezone"""
    while True:
        try:
            line = sio.readline()
            msg = pynmea2.parse(line)

            if type(msg) == pynmea2.types.talker.RMC:

                status = msg.status

                if status == 'V':
                    logger.debug('Wait for active state')
                    time.sleep(0.1)

                if status == 'A':
                    logger.debug('Got Fix')

                    zeit = msg.datetime

                    latitude = msg.latitude
                    longitude = msg.longitude

                    tf = TimezoneFinder()
                    zeitzone_string = tf.timezone_at (lat=latitude, lng=longitude)

                    logger.debug('Set timezone to %s', zeitzone_string)
                    os.system(f"timedatectl set-timezone {zeitzone_string}")

                    zeitzone = pytz.timezone(zeitzone_string)
                    zeit_mit_zeitzone = zeit.replace(tzinfo=pytz.utc).astimezone(zeitzone)
                    unix_zeit = time.mktime(zeit_mit_zeitzone.timetuple())

                    logger.debug('Set time to %s', zeit_mit_zeitzone)
                    clk_id = time.CLOCK_REALTIME
                    time.clock_settime(clk_id, float(unix_zeit))

                    break

        except serial.SerialException as e:
            logger.error('Device error: {}'.format(e))
            break
        except pynmea2.ParseError as e:
            logger.error('Parse error: {}'.format(e))
        except UnicodeDecodeError as e:
            logger.error('UnicodeDecodeError error: {}'.format(e))

        continue

#Parse and print gps data
def print_data():
    """Parse and print gps data"""
    while True:   
        try:
            line = sio.readline()
            msg = pynmea2.parse(line)
            if type(msg) == pynmea2.types.talker.RMC:

                zeit = msg.datetime
                latitude = float(msg.latitude)
                longitude = float(msg.longitude)
                speed = float(msg.spd_over_grnd)
                course = msg.true_course

                speed_kph = float(speed)*1.852

                print("time: ", zeit,"(UTC)",'\n')
                print("lat in degrees:", round(float(latitude),8)," long in degree: ", round(float(longitude),8), '\n')
                print("speed over ground: ", round(float(speed_kph),1),"kph",'\n')
                print("course over ground: ", course,"degrees",'\n')
                print("------------------------------------------------------------\n")

        except serial.SerialException as e:
            logger.error('Device error: {}'.format(e))
            break
        except pynmea2.ParseError as e:
            logger.error('Parse error: {}'.format(e))
        except UnicodeDecodeError as e:
            logger.error('UnicodeDecodeError error: {}'.format(e))

#Logger setting
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

#Serial setting
uart = serial.Serial(port = '/dev/ttyS0', baudrate = 115200, timeout=0.1)
sio = io.TextIOWrapper(io.BufferedRWPair(uart, uart))

wait_active_set_time()

try:
    print_data()

except KeyboardInterrupt:
    sys.exit(0)