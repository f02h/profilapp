import tkinter as tk
import serial
import json
import sqlite3
from tkinter import *
from tkinter import ttk



USB_PORT = "/dev/ttyACM0"
usb = serial.Serial(USB_PORT, 115200)

conn = sqlite3.connect('/home/pi/profil/todo.db')
c = conn.cursor()

class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        self._geom='200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        master.bind('<Escape>',self.toggle_geom)
    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom


def submitForm():
    strFile = optVariable.get()
    # Print the selected value from Option (Combo Box)
    if (strFile !=''):
        print('Selected Value is : ' + strFile)

def write_slogan():
    print("Tkinter is easy to use!")

def hear():
    msg = usb.read_until() # read until a new line
    mystring = msg.decode('ascii')  # decode n return
    return mystring

def callback(*args):
    res = c.execute("SELECT id,name FROM profili WHERE name LIKE ?", (str(monthchoosen.get()))).fetchall()
    result = c.fetchone()
    idProfil = float(result[0])
    if not idProfil:
        idProfil = 1

    res = c.execute("SELECT name,value FROM vars WHERE idProfil LIKE ?", (str(idProfil))).fetchall()
    dbvars = dict(res)

    i=0
    for var in dbvars:
        tk.Label(tab2, text="{var}").grid(row=i)
        e1 = tk.Entry(tab2)
        e1.grid(row=i, column=1)
        e1.insert(0,dbvars[var])
        i+=1


    print(f"the variable has changed to '{profilList[monthchoosen.get()]}'")


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
    label.config(text=str(hearv))

def home():

    data = {
        "action": "home",
    }

    usb.write(json.dumps(data).encode())
    hearv = hear()
    label.config(text=str(hearv))

root = tk.Tk()
app=FullScreenApp(root)
tabControl = ttk.Notebook(root)

tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)

tabControl.add(tab1, text='Vrtalka')
tabControl.add(tab2, text='Nastavitve')
tabControl.pack(expand=1, fill="both")

button = tk.Button(tab1,
                   text="QUIT",
                   fg="red",
                   command=quit).grid(column=0,
                               row=0,
                               padx=30,
                               pady=30)
drill = tk.Button(tab1,
                   text="Drill",
                   command=drill).grid(column=1,
                               row=0,
                               padx=30,
                               pady=30)

homing = tk.Button(tab1,
                   text="Homing",
                   command=home).grid(column=2,
                               row=0,
                               padx=30,
                               pady=30)

res = c.execute("SELECT id,name FROM profili").fetchall()
profilList = dict(res)


n = tk.StringVar()
n.trace("w", callback)
monthchoosen = ttk.Combobox(tab2, width=27,
                            textvariable=n)
# Adding combobox drop down list
monthchoosen['values'] = list(profilList.values())
monthchoosen.grid(column=1, row=15)


Button(tab2, text='Submit', command=submitForm, width=20,bg='brown',fg='white').place(x=100,y=100)



label = tk.Label(root, fg="dark green")
label.pack()

root.mainloop()
