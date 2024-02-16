import os
from time import sleep
import subprocess
import re

def get_mac_address():
    """Get MAC adress of SIGHTER RC"""
    output = subprocess.check_output(["bluetoothctl", "devices"]).decode("utf-8")
    pattern = r"Device\s+([^\s]+)\s+SIGHTER RC"
    match = re.search(pattern, output)
    if match:
        return match.group(1)
    else:
        return None

def remove_devices_except_keyboard():
    """Remove all Bluetooth devices except SIGHTER RC"""
    keyboard_mac = get_mac_address()
    #If remote detected
    if keyboard_mac is not None:
        output = subprocess.check_output(["bluetoothctl", "devices"]).decode("utf-8")
        pattern = r"Device\s+([^\s]+)\s+.*"
        matches = re.findall(pattern, output)
        for device_mac in matches:
            if device_mac != keyboard_mac:
                command = f"bluetoothctl remove {device_mac}"
                os.system(command)
                print(f"Removed Bluetooth device: {device_mac}")
    #If remote not detected
    else:
        os.system('for device in $(bluetoothctl devices  | grep -o "[[:xdigit:]:]\{8,17\}"); do echo "removing bluetooth device: $device | $(bluetoothctl remove $device)"; done')
        print(f"Removed All Bluetooth devices")

#Pairmode on
def pairmode_on():
    os.system('bluetoothctl discoverable on')
    sleep(0.5)
    os.system('bluetoothctl pairable on')

#Pairmode off
def pairmode_off():
    os.system('bluetoothctl discoverable off')
    sleep(0.5)
    os.system('bluetoothctl pairable off')

def main():
    remove_devices_except_keyboard()
    sleep(0.5)
    pairmode_on()
    sleep(30)
    pairmode_off()


if __name__ == '__main__':
    main()
