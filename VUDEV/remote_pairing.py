import subprocess
import datetime as dt
from time import sleep
import re
import time
import os
import RPi.GPIO as GPIO

def remove_devices():
  """Remove all bluetooth devices"""
  os.system('for device in $(bluetoothctl devices  | grep -o "[[:xdigit:]:]\{8,17\}"); do echo "removing bluetooth device: $device | $(bluetoothctl remove $device)"; done')

def get_mac_address():
  """Get MAC adress of SIGHTER RC"""
  output = subprocess.check_output(["bluetoothctl", "devices"]).decode("utf-8")

  pattern = r"Device\s+([^\s]+)\s+SIGHTER RC"
  match = re.search(pattern, output)
  if match:
    return match.group(1)
  else:
    return None

def pair_and_trust(mac_address):
  """Pair and trust device"""
  if mac_address:
    subprocess.run(["bluetoothctl", "pair", mac_address])
    subprocess.run(["bluetoothctl", "trust", mac_address])
    print("Device paired and trusted successfully.")
  else:
    print("SIGHTER RC device not found.")

def main():

  os.system('sudo rfkill block wifi')

  remove_devices()

  # scan on
  bt_proc = subprocess.Popen(["bluetoothctl"], stdin=subprocess.PIPE)
  bt_proc.stdin.write(b"scan on\n")
  bt_proc.stdin.flush()

  # SIGHTER RC detection
  keyboard_mac_address = None
  while not keyboard_mac_address:
    keyboard_mac_address = get_mac_address()
    time.sleep(1)

  # scan off
  bt_proc.stdin.write(b"scan off\n")
  bt_proc.stdin.flush()
  bt_proc.stdin.close()
  bt_proc.wait()

  pair_and_trust(keyboard_mac_address)

  os.system('sudo rfkill unblock wifi')

def keymap():
  """BT Controller pairing"""

  GPIO.setmode(GPIO.BCM)
  GPIO.setwarnings(False)
  GPIO.setup([17], GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

  while True:
    sleep(0.1)

    if GPIO.input(17) == 1:
        pairbtntime = dt.datetime.now()
        button_released = False

        # Button press time >= 2 seconds
        while (dt.datetime.now() - pairbtntime).seconds < 2:
            if GPIO.input(17) == 0:
                button_released = True
                break
            sleep(0.1)

        if not button_released:  
            print('Controller pairing start')
            main()
            print('Controller pairing done')

if __name__ == "__main__":
  keymap()
