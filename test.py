import tkinter as tk
import serial
import json
import sqlite3
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import os, time
from threading import Thread

USB_PORT_FEEDER = "/dev/ttyUSB0"
#usbf = serial.Serial(USB_PORT_FEEDER, 115200)
usbf = serial.Serial(
    port=USB_PORT_FEEDER, baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
)

def moveFeeder(dir, step, abs=0, firstMove=0):

   idProfil = 1

   # 44.44
   data = {
      "A": str(dir),
      "M": str(int(step * 44.44)),
      "M2": abs,
      "P": idProfil,
      "F": firstMove
   }

   usbf.write(json.dumps(data).encode())
   hearv = hearJsonf()
   # print(hearv)
   return hearv["status"]


def hearJsonf():
   # msg = usbf.read_until()# read until a new line
   # mystring = json.loads(str(msg.decode("Ascii")).strip())
   # return mystring

   while 1:
      if usbf.in_waiting > 0:

         # Read data out of the buffer until a carraige return / new line is found
         serialString = usbf.readline()

         # Print the contents of the serial data
         try:
            # print(serialString.decode("Ascii"))

            mystring = json.loads(str(serialString.decode("Ascii")).strip())
            # print(mystring)
            return mystring
         except:
            print("fail")
            pass


def homeFeeder():
   data = {
      "A": "home"
   }

   usbf.write(json.dumps(data).encode())
   hearv = hearJsonf()

homeFeeder()
tmpStatus = moveFeeder("moveRev", float(200), 1, 1)