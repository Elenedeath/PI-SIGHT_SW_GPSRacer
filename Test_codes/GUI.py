import sys

from PyQt5.QtWidgets import *
from PyQt5 import uic
import pyautogui

import BT_pair as bt

#Import UI file
form_class = uic.loadUiType("/boot/VUDEV/GPSreceiver-1.ui")[0]
#form_class = uic.loadUiType("C:\Python37/GPSreceiver-1.ui")[0]

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        #button-fuction connect
        self.pairbutton.clicked.connect(self.pairFunction)

    #pairbutton action
    def pairFunction(self) :
        bt.main()


if __name__ == "__main__" :
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    myWindow = WindowClass() 
    myWindow.show()

    #Auto click when startup for focus effect
    pyautogui.moveTo(20, 20)
    pyautogui.click()
    
    app.exec_()