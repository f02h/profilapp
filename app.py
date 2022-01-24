import tkinter as tk
import serial
import json
import sqlite3



USB_PORT = "/dev/ttyACM0"
usb = serial.Serial(USB_PORT, 115200)

conn = sqlite3.connect('/home/pi/profil/todo.db')
c = conn.cursor()

def write_slogan():
    print("Tkinter is easy to use!")

def hear():
    msg = usb.read_until() # read until a new line
    mystring = msg.decode('ascii')  # decode n return
    return mystring


def drill():
    res = c.execute("SELECT name,value FROM vars").fetchall()
    dictionary = {}
    # dbvars = (Convert(res, dictionary))
    dbvars = dict(res)

    ## pozicijaLNull
    ## pozicijaDNull
    ## pozicijaL
    ## pozicijaD
    ## orodjeL
    ## orodjeD
    ## hodL
    ## počasnejePredKoncemHodaL
    ## hitrostPredKoncemHodaL
    ## hodD
    ## počasnejePredKoncemHodaD
    ## hitrostPredKoncemHodaD
    ## povratekL
    ## povratekD
    ## povrtavanjeL
    ## povrtavanjeD

    data = {
        "A": "drill",
        "PLN": dbvars["pozicijaLNull"] * 160,
        "PDN": dbvars["pozicijaDNull"] * 160,
        "PL": dbvars["pozicijaL"] * 160,
        "PD": dbvars["pozicijaD"] * 160,
        "OL": dbvars["orodjeL"],
        "OD": dbvars["orodjeD"],
        "HL": dbvars["hodL"] * 160,
        "PHL": dbvars["pocasnejePredKoncemHodaL"],
        "PHLH": dbvars["hitrostPredKoncemHodaL"],
        "HD": dbvars["hodD"] * 160,
        "PHD": dbvars["pocasnejePredKoncemHodaD"],
        "PHDH": dbvars["hitrostPredKoncemHodaD"],
        "POL": dbvars["povratekL"] * 160,
        "POD": dbvars["povratekD"] * 160,
        "POVL": dbvars["povrtavanjeL"] * 160,
        "POVD": dbvars["povrtavanjeD"] * 160,
    }

    usb.write(json.dumps(data).encode())
    hearv = hear()

def home():

    data = {
        "action": "home",
    }

    usb.write(json.dumps(data).encode())
    hearv = hear()

root = tk.Tk()
frame = tk.Frame(root)
frame.pack()

button = tk.Button(frame,
                   text="QUIT",
                   fg="red",
                   command=quit)
button.pack(side=tk.LEFT)
drill = tk.Button(frame,
                   text="Drill",
                   command=drill)
drill.pack(side=tk.LEFT)
homing = tk.Button(frame,
                   text="Homing",
                   command=home)
homing.pack(side=tk.LEFT)

root.mainloop()
