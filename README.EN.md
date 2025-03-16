# PI-SIGHT SW - GPS Racer

'GPS Racer' allows [PI-SIGHT](https://github.com/younsj97/PI-SIGHT_Helmet_HUD) to be used as a lap timer or a Bluetooth GPS receiver that can be linked to a smartphone, and the part related to measuring and recording lap times was created using the [Exit_Speed](https://github.com/djhedges/exit_speed) software.


## function

 - Receives 10Hz GPS data via PI-SIGHT’s external GPS module.
 - When using receiver mode, PI-SIGHT becomes an external GPS module that connects to a smartphone via Bluetooth and transmits 10Hz GPS data, and can be registered as an external GPS device in the RaceChrono app.
 - When using Lap Timer mode, PI-SIGHT automatically finds the nearest track using its own GPS data, records lap times, and outputs the current time difference compared to your best lap time in real time.
 - For more information, please visit the [VUDEV website](https://sites.google.com/vudev.net/vudevnet/gpsracer-info) or download the [manual](https://github.com/younsj97/PI-SIGHT_SW_GPSRacer/blob/main/PI-SIGHT%20%EC%82%AC%EC%9A%A9%EC%84%A4%EB%AA%85%EC%84%9C-4%20(GPS%EB%A0%88%EC%9D%B4%EC%84%9C).pdf).


## installation

 1. Download and install the [Raspberry Pi imager](https://www.raspberrypi.com/software/) app.
 2. After downloading the [software file](http://naver.me/G1w16QKO), unzip it to create the GPSRacer-16GB-yymmdd.img file.
 3. Run the Raspberry Pi imager, connect the MicroSD to the PC, and select Erase to format the memory.
 4. Once formatting is complete, select Use Custom and select the GPSRacer-16GB-yymmdd.img file. (Do not use any custom settings including SSH.)


## caution

 - _The rear camera does not work due to GPS signal interference._
 - _GPSRacer-16GB-yymmdd.img firmware can be installed on 16GB microSD memory._
 - If you want to increase the boot partition size by using a memory card larger than 32GB, install the 16GB firmware first, then [increase the boot partition size using GParted.](https://learn.adafruit.com/resizing-raspberry-pi-boot-partition/edit-partitions)_


## Customizing

 - If you want to apply the PI-SIGHT GPS Racer system from the basic Raspberry pi OS, please refer to the [setup method](https://vudev.notion.site/GPS-Racer-7e79e486b4ea4caca37722aa5a25803d?pvs=4).