#!/bin/bash

sleep 0.5

sudo python3 /boot/VUDEV/GPSracer_controller-noncam.py &

sudo rfkill block wifi
#sudo rfkill unblock wifi

#Bluetooth controller pairing function
sudo python3.7 /boot/VUDEV/remote_pairing.py &

sleep 10

#Bluetooth agent NoInputNoOutput problem solver
sudo bt-agent --capability=DisplayOnly -p /home/pi/pins &