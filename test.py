import tkinter as tk
import serial
import json
import sqlite3
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import os




USB_PORT = "/dev/ttyACM0"
USB_PORT_FEEDER = "/dev/ttyUSB1"
usb = serial.Serial(USB_PORT, 115200)
usbf = serial.Serial(USB_PORT_FEEDER, 115200)
#usb = 0
#usbf = 0
path = os.path.dirname(os.path.abspath(__file__))
db = os.path.join(path, 'todo.db')

conn = sqlite3.connect(db)
c = conn.cursor()

settingsList = dict()
currentSetting = None

stepperList = {1:0,2:0,3:0,4:0,5:0,6:0,7:0}
spindleList = {1:0,2:0,3:0,4:0,5:0,6:0,7:0}

sensorToDrill = 0

def hearJsonf():
    msg = usbf.read_until()# read until a new line
    mystring = json.loads(str(msg.decode("utf-8")).strip())
    return mystring

def moveFeeder(dir, step):

    data = {
        "A": str(dir),
        "M": int(float(step)) *160,
        "P": 1
    }

    usbf.write(json.dumps(data).encode())
    hearv = hearJsonf()
    """print(hearv)
    if str(hearv["status"]).strip() == "done":
        #cut.config(state=ACTIVE, bg='green')
    else:
        #cut.config(state=ACTIVE, bg='red')
    label.config(text=str(hearv))
"""


def homeFeeder():
    data = {
        "A": "home"
    }

    usbf.write(json.dumps(data).encode())
    hearv = hearJsonf()
    if str(hearv["status"]).strip() == "done":
        print('done')
    else:
        print('fail')

