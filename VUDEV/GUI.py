#!/usr/bin/python3

import sys
import threading
import os
from time import sleep

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QDateTime, QTimer
import pyautogui
from absl import app
import pyscreenshot

import BT_pair as bt
import sighter_init
import sighter_receiver
import exit_speed_main
import BT_detect

#Import UI file
form_class = uic.loadUiType("/boot/VUDEV/gps_racer-1.ui")[0]
#form_class = uic.loadUiType("/home/pi/VUDEV/gps_racer-1.ui")[0]

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()

        self.setupUi(self)

        '''Set GPStimer'''
        self.gpstimer = QTimer(self)
        self.gpstimer.setInterval(1000)
        self.gpstimer.timeout.connect(self.gpstime)

        '''State tab Widgets / fuction'''
        self.datetime_label.setText("Connect controller and fix GPS")
        self.fixgpsbutton.clicked.connect(self.fixgpsFunction)
        self.pairbutton.clicked.connect(self.pairFunction)

        '''Set remote connection state label'''
        bt_detect_thread = threading.Thread(target=BT_detect.main, args=())
        bt_detect_thread.start()
        self.remote_state_timer = QTimer()
        self.remote_state_timer.setInterval(1000)
        self.remote_state_timer.timeout.connect(self.update_remote_state_label)
        self.remote_state_timer.start()

        '''Receiver Mode tab Widgets / fuction'''
        self.receiver_startbutton.clicked.connect(self.receiver_startFunction)
        self.receiver_startbutton.setEnabled(False)
        self.receiver_stopbutton.clicked.connect(self.receiver_stopFunction)
        self.receiver_stopbutton.setEnabled(False)

        '''Set speedometer'''
        self.speedometer_timer = QTimer()
        self.speedometer_timer.setInterval(200)
        self.speedometer_timer.timeout.connect(self.update_nowspeed_label)

        self.speedunit_label.setStyleSheet("Color : red")

        '''Set best speed'''
        self.bestspeed_timer = QTimer()
        self.bestspeed_timer.setInterval(200)
        self.bestspeed_timer.timeout.connect(self.update_bestspeed_label)

        '''Laptime Mode tab Widgets / fuction'''
        self.laptime_startbutton.clicked.connect(self.laptime_startFunction)
        self.laptime_startbutton.clicked.connect(self.session_info_startFunction)
        self.laptime_startbutton.clicked.connect(self.lap_info_startFunction)
        self.laptime_startbutton.setEnabled(False)
        self.laptime_stopbutton.clicked.connect(self.laptime_stopFunction)
        self.laptime_stopbutton.clicked.connect(self.session_info_stopFunction)
        self.laptime_stopbutton.clicked.connect(self.lap_info_stopFunction)
        self.laptime_stopbutton.setEnabled(False)

        self.lapnumber_timer = QTimer()
        self.lapnumber_timer.setInterval(200)
        self.lapnumber_timer.timeout.connect(self.update_lapnumber_label)

        self.comparedata_timer = QTimer()
        self.comparedata_timer.setInterval(100)
        self.comparedata_timer.timeout.connect(self.update_comparedata_label)

        self.bestlaptime_timer = QTimer()
        self.bestlaptime_timer.setInterval(200)
        self.bestlaptime_timer.timeout.connect(self.update_bestlaptime_label)

        self.compareunit_label.setStyleSheet("Color : red")

        '''Session Info tab Widgets / fuction'''
        self.info_trackname_timer = QTimer()
        self.info_trackname_timer.setInterval(1000)
        self.info_trackname_timer.timeout.connect(self.update_trackname_info_label)

        self.info_vehicle_timer = QTimer()
        self.info_vehicle_timer.setInterval(1000)
        self.info_vehicle_timer.timeout.connect(self.update_vehicle_info_label)

        self.info_lapnumber_timer = QTimer()
        self.info_lapnumber_timer.setInterval(1000)
        self.info_lapnumber_timer.timeout.connect(self.update_lapnumber_info_label)

        self.info_bestlaptime_timer = QTimer()
        self.info_bestlaptime_timer.setInterval(1000)
        self.info_bestlaptime_timer.timeout.connect(self.update_bestlaptime_info_label)

        self.info_bestspeed_timer = QTimer()
        self.info_bestspeed_timer.setInterval(1000)
        self.info_bestspeed_timer.timeout.connect(self.update_bestspeed_info_label)

        self.session_info_savebutton.clicked.connect(self.session_info_saveFunction)
        self.session_info_savebutton.setEnabled(False)

        '''Lap Info tab Widgets / fuction'''

        self.lap_record_timer = QTimer()
        self.lap_record_timer.setInterval(1000)
        self.lap_record_timer.timeout.connect(self.update_lap_record_label)

        self.lap_info_savebutton.clicked.connect(self.lap_info_saveFunction)
        self.lap_info_savebutton.setEnabled(False)

        root_path = os.getenv("ROOT_PATH", "/boot")
        #root_path = os.getenv("ROOT_PATH", "/home/pi")
        dir_path = os.getenv("RECORDINGS_PATH", "Saved_Data")
        self.data_capture_path = os.path.join(root_path, dir_path)

## Setting tab

    '''display datetime'''
    def gpstime(self):
        currentDateTime = QDateTime.currentDateTime().toString("yy.MM.dd-hh:mm:ss")
        self.datetime_label.setText(currentDateTime)

    '''GPS button action'''
    def fixgpsFunction(self) :
        self.gpstimer.start()
        fixgpsthread = threading.Thread(target=self.during_fixgps, args=())
        fixgpsthread.start()

    def during_fixgps(self) :
        self.datetime_label.setText('Waiting GPS...')
        self.datetime_label.setStyleSheet("Color : red")
        self.fixgpsbutton.setEnabled(False)
        self.fixgpsbutton.setText('Waiting..')
        sighter_init.wait_active_set_time()
        self.datetime_label.setStyleSheet("Color : lightgreen")
        self.fixgpsbutton.setEnabled(True)
        self.fixgpsbutton.setText('Fix GPS')
        self.receiver_startbutton.setEnabled(True)
        self.laptime_startbutton.setEnabled(True)

    '''Pair button action'''
    def pairFunction(self) :
        pairthread = threading.Thread(target=self.during_pair, args=())
        pairthread.start()

    def during_pair(self) :
        self.pairbutton.setEnabled(False)
        self.pairbutton.setText('Pairing..')
        self.receiver_startbutton.setEnabled(False)
        bt.main()
        self.pairbutton.setEnabled(True)
        self.pairbutton.setText('Pair Phone')
        self.receiver_startbutton.setEnabled(True)

    def update_remote_state_label(self):
        connection = BT_detect.get_check_connection()

        if connection == 1 :
            self.remote_state_label.setText("Connected")
            self.remote_state_label.setStyleSheet("Color : lightgreen")

        else :
            self.remote_state_label.setText("Disconnected")
            self.remote_state_label.setStyleSheet("Color : red")

## Receiver Mode tab

    '''Receiver mode action'''
    def receiver_startFunction(self) :
        self.fixgpsbutton.setEnabled(False)
        self.pairbutton.setEnabled(False)
        self.receiver_startbutton.setEnabled(False)
        self.receiver_stopbutton.setEnabled(True)
        self.speedunit_label.setStyleSheet("Color : white")
        self.laptime_startbutton.setEnabled(False)
        receiver_start = threading.Thread(target=sighter_receiver.main, args=())
        receiver_start.start()
        self.speedometer_timer.start()
        self.bestspeed_timer.start()

    def receiver_stopFunction(self) :
        self.speedometer_timer.stop()
        self.bestspeed_timer.stop()
        sighter_receiver.termination()
        self.fixgpsbutton.setEnabled(True)
        self.pairbutton.setEnabled(True)
        self.receiver_startbutton.setEnabled(True)
        self.receiver_stopbutton.setEnabled(False)
        self.nowspeed_label.setText("888")
        self.speedunit_label.setStyleSheet("Color : red")
        self.laptime_startbutton.setEnabled(True)

    def update_nowspeed_label(self):
        nowspeed_kph = sighter_receiver.get_nowspeed_kph()
        if nowspeed_kph < 0.5 :
            nowspeed_kph = 0
        self.nowspeed_label.setText(str(nowspeed_kph))

    def update_bestspeed_label(self):
        bestspeed_kph = sighter_receiver.get_bestspeed_kph()
        self.bestspeed_label.setText("Best speed: " + str(bestspeed_kph) + " kph")

## Laptime Mode tab

    '''Laptime mode action'''
    def laptime_startFunction(self) :
        self.fixgpsbutton.setEnabled(False)
        self.pairbutton.setEnabled(False)
        self.receiver_startbutton.setEnabled(False)
        self.laptime_startbutton.setEnabled(False)
        self.laptime_stopbutton.setEnabled(True)
        self.compareunit_label.setStyleSheet("Color : white")
        exitspeed_thread = threading.Thread(target=exit_speed_main.start, args=())
        exitspeed_thread.start()
        self.lapnumber_timer.start()
        self.comparedata_timer.start()
        self.bestlaptime_timer.start()

    def laptime_stopFunction(self) :
        self.lapnumber_timer.stop()
        self.comparedata_timer.stop()
        self.bestlaptime_timer.stop()
        exit_speed_main.termination()
        self.fixgpsbutton.setEnabled(True)
        self.pairbutton.setEnabled(True)
        self.receiver_startbutton.setEnabled(True)
        self.laptime_startbutton.setEnabled(True)
        self.laptime_stopbutton.setEnabled(False)
        self.compareunit_label.setStyleSheet("Color : red")

    def update_lapnumber_label(self) :
        lapnumber = exit_speed_main.get_lap_number()
        self.lapnumber_label.setText(str(lapnumber))

    def update_comparedata_label(self) :
        lapnumber = exit_speed_main.get_lap_number()
        if lapnumber >= 3 :
          comparedata = exit_speed_main.get_time_compare_data()
          if comparedata < 0:
            self.comparedata_label.setStyleSheet("Color : lightgreen")
          else:
            self.comparedata_label.setStyleSheet("Color : yellow")
          comparedata_rounded = round(float(comparedata),1)
          self.comparedata_label.setText(str(comparedata_rounded))

    def update_bestlaptime_label(self) :
        bestlaptime_minutes = exit_speed_main.get_bestlap_minutes()
        bestlaptime_seconds = exit_speed_main.get_bestlap_seconds()
        bestlaptime = '%02d:%06.3f' % (bestlaptime_minutes, bestlaptime_seconds)
        self.bestlaptime_label.setText("Best Lap Time: " + str(bestlaptime))

## Session Info tab

    def session_info_startFunction(self) :
        self.info_trackname_timer.start()
        self.info_vehicle_timer.start()
        startDateTime = QDateTime.currentDateTime().toString("yy.MM.dd-hh:mm:ss")
        self.starttime_info_label.setText("Start Time: " + str(startDateTime))
        self.endtime_info_label.setText("End Time: ")
        self.info_lapnumber_timer.start()
        self.info_bestlaptime_timer.start()
        self.info_bestspeed_timer.start()
        self.session_info_savebutton.setEnabled(False)
        self.sessionstart_datetime = QDateTime.currentDateTime().toString("yy.MM.dd-hh.mm.ss")

    def session_info_stopFunction(self) :
        self.info_trackname_timer.stop()
        self.info_vehicle_timer.stop()
        endDateTime = QDateTime.currentDateTime().toString("yy.MM.dd-hh:mm:ss")
        self.endtime_info_label.setText("End Time: " + str(endDateTime))
        self.info_lapnumber_timer.stop()
        self.info_bestlaptime_timer.stop()
        self.info_bestspeed_timer.stop()
        self.session_info_savebutton.setEnabled(True)
    
    def update_trackname_info_label(self) :
        trackname = exit_speed_main.get_trackname()
        self.trackname_info_label.setText("Track: " + str(trackname))

    def update_lapnumber_info_label(self) :
        lapnumber = exit_speed_main.get_lap_number()
        lapnumber_info = lapnumber - 1
        self.lapnumber_info_label.setText("Laps: " + str(lapnumber_info))

    def update_vehicle_info_label(self) :
        carname = exit_speed_main.get_carname()
        self.vehicle_info_label.setText("Vehicle: " + str(carname))

    def update_bestlaptime_info_label(self) :
        bestlaptime_minutes = exit_speed_main.get_bestlap_minutes()
        bestlaptime_seconds = exit_speed_main.get_bestlap_seconds()
        bestlaptime = '%02d:%06.3f' % (bestlaptime_minutes, bestlaptime_seconds)
        self.bestlaptime_info_label.setText("Best Laptime: " + str(bestlaptime))

    def update_bestspeed_info_label(self) :
        bestspeed = exit_speed_main.get_bestspeed()
        self.bestspeed_info_label.setText("Best Speed: " + str(bestspeed) + " kph")

    def session_info_saveFunction(self) :
        self.session_info_savebutton.setEnabled(False)

        if not os.path.exists(self.data_capture_path):
            os.mkdir(self.data_capture_path)

        trackname = exit_speed_main.get_trackname()

        session_img = pyscreenshot.grab()
        session_img.save('%s/%s_%s_Session.png' % (self.data_capture_path,trackname,self.sessionstart_datetime))

        #os.system('sudo rm -r /boot/lap_logs')
        
        sleep (0.5)

        self.session_info_savebutton.setEnabled(True)

## Lap Info tab

    def lap_info_startFunction(self) :
        self.lap1_record_label.setText("Lap 1 : 00:00:000")
        self.lap2_record_label.setText("Lap 2 : 00:00:000")
        self.lap3_record_label.setText("Lap 3 : 00:00:000")
        self.lap4_record_label.setText("Lap 4 : 00:00:000")
        self.lap5_record_label.setText("Lap 5 : 00:00:000")
        self.lap6_record_label.setText("Lap 6 : 00:00:000")
        self.lap7_record_label.setText("Lap 7 : 00:00:000")
        self.lap8_record_label.setText("Lap 8 : 00:00:000")
        self.lap_record_timer.start()
        self.lap_info_savebutton.setEnabled(False)

    def lap_info_stopFunction(self) :
        self.lap_record_timer.stop()
        self.lap_info_savebutton.setEnabled(True)

    def update_lap_record_label(self) :
        lapnumber = exit_speed_main.get_lap_number()
        laptime_minutes = exit_speed_main.get_lap_minutes()
        laptime_seconds = exit_speed_main.get_lap_seconds()
        laptime = '%02d:%06.3f' % (laptime_minutes, laptime_seconds)
        if lapnumber == 2 :
            self.lap1_record_label.setText("Lap1 : " + str(laptime))
        if lapnumber == 3 :
            self.lap2_record_label.setText("Lap2 : " + str(laptime))
        if lapnumber == 4 :
            self.lap3_record_label.setText("Lap3 : " + str(laptime))
        if lapnumber == 5 :
            self.lap4_record_label.setText("Lap4 : " + str(laptime))
        if lapnumber == 6 :
            self.lap5_record_label.setText("Lap5 : " + str(laptime))
        if lapnumber == 7 :
            self.lap6_record_label.setText("Lap6 : " + str(laptime))
        if lapnumber == 8 :
            self.lap7_record_label.setText("Lap7 : " + str(laptime))
        if lapnumber == 9 :
            self.lap8_record_label.setText("Lap8 : " + str(laptime))

    def lap_info_saveFunction(self) :
        self.lap_info_savebutton.setEnabled(False)

        if not os.path.exists(self.data_capture_path):
            os.mkdir(self.data_capture_path)

        trackname = exit_speed_main.get_trackname()
        
        laps_img = pyscreenshot.grab()
        laps_img.save('%s/%s_%s_Laps.png' % (self.data_capture_path,trackname,self.sessionstart_datetime))

        #os.system('sudo rm -r /boot/lap_logs')

        sleep (0.5)

        self.lap_info_savebutton.setEnabled(True)


def main(unused_argv):
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    myWindow = WindowClass()
    myWindow.showFullScreen()

    '''Auto click when startup for focus effect'''
    pyautogui.moveTo(20, 20)
    pyautogui.click()

    app.exec_()

if __name__ == "__main__" :
    app.run(main)
