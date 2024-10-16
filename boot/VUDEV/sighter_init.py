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

    #Set Logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    #Set GPS serial port
    uart = serial.Serial(port = '/dev/ttyS0', baudrate = 115200, timeout=0.1)
    sio = io.TextIOWrapper(io.BufferedRWPair(uart, uart))

    while True:
        try:
            line = sio.readline()
            msg = pynmea2.parse(line)

            if type(msg) == pynmea2.types.talker.RMC:

                status = msg.status

                #GPS inactive state
                if status == 'V':
                    logger.debug('Wait for active state')
                    time.sleep(0.5)

                #GPS active state
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


if __name__ == '__main__':
    wait_active_set_time()
