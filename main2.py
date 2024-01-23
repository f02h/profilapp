import tkinter as tk
import serial
import json
import sqlite3
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import os, time
from threading import Thread
from PIL import Image,ImageTk

t = 'test'
USB_PORT = "/dev/ttyACM0"
USB_PORT_FEEDER = "/dev/ttyUSB1"
USB_PORT_LOADER = "/dev/ttyUSB0"
usb = serial.Serial(USB_PORT, 115200)
#usbf = serial.Serial(USB_PORT_FEEDER, 115200)
usbf = serial.Serial(port=USB_PORT_FEEDER, baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
usbl = serial.Serial(port=USB_PORT_LOADER, baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
#usb = 0
#usbf = 0
#usbl = 0
path = os.path.dirname(os.path.abspath(__file__))
db = os.path.join(path, 'todo.db')

conn = sqlite3.connect(db, check_same_thread=False)
c = conn.cursor()

settingsList = dict()
currentSetting = None
jobsRunning = False

stepperList = {1:0,2:0,3:0,4:0,5:0,6:0,7:0}
spindleList = {1:0,2:0,3:0,4:0,5:0,6:0,7:0}

#sensorToDrill = 197.4
## add to settings page
# + premakne prva luknja bolj naprej
# - premakne prvo luknjo bolj nazaj
# razdalja žaga - sveder
#sensorToDrill = 30.85
sensorToDrill = 23
currentSensorToDrill = 0.0

#refZaga
# + premakne prva luknja bolj nazaj
# - premakne prvo luknjo bolj naprej
balansRef = 18.9

#
# razdalja referenca - žaga
#refExtension = 260
refExtension = 250
feederRef = 225
extensionLength = 370
currentCutLen = 0

#debelina zage
saw_width = 2.5

changingLen = False
stop_auto_thread = False
cycleThread = None
cycleAutoThread = None
currentProfileId = None
currentQty = 0
currentQtyLabel = 0
manualLoading = False
disableDrill = False

def enumerate_row_column(iterable, num_cols):
    for idx, item in enumerate(iterable):
        row = idx // num_cols
        col = idx % num_cols
        yield row, col, item

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
FIT_WIDTH = "fit_width"
FIT_HEIGHT = "fit_height"


class ScrollableFrame(tk.Frame):
    """
    There is no way to scroll <tkinter.Frame> so we are
    going to create a canvas and place the frame there.
    Scrolling the canvas will give the illusion of scrolling
    the frame
    Partly taken from:
        https://blog.tecladocode.com/tkinter-scrollable-frames/
        https://stackoverflow.com/a/17457843/11106801
    master_frame---------------------------------------------------------
    | dummy_canvas-----------------------------------------  y_scroll--  |
    | | self---------------------------------------------  | |         | |
    | | |                                                | | |         | |
    | | |                                                | | |         | |
    | | |                                                | | |         | |
    | |  ------------------------------------------------  | |         | |
    |  ----------------------------------------------------   ---------  |
    | x_scroll---------------------------------------------              |
    | |                                                    |             |
    |  ----------------------------------------------------              |
     --------------------------------------------------------------------
    """
    def __init__(self, master=None, scroll_speed:int=2, hscroll:bool=False,
                 vscroll:bool=True, bd:int=0, scrollbar_kwargs={},
                 bg="#f0f0ed", **kwargs):
        assert isinstance(scroll_speed, int), "`scroll_speed` must be an int"
        self.scroll_speed = scroll_speed

        self.master_frame = tk.Frame(master, bd=bd, bg=bg)
        self.master_frame.grid_rowconfigure(0, weight=1)
        self.master_frame.grid_columnconfigure(0, weight=1)
        self.dummy_canvas = tk.Canvas(self.master_frame, highlightthickness=0,
                                      bd=0, bg=bg, **kwargs)
        super().__init__(self.dummy_canvas, bg=bg)

        # Create the 2 scrollbars
        if vscroll:
            self.v_scrollbar = tk.Scrollbar(self.master_frame,
                                            orient="vertical",
                                            command=self.dummy_canvas.yview,
                                            **scrollbar_kwargs)
            self.v_scrollbar.grid(row=0, column=1, sticky="news")
            self.dummy_canvas.configure(yscrollcommand=self.v_scrollbar.set)
        if hscroll:
            self.h_scrollbar = tk.Scrollbar(self.master_frame,
                                            orient="horizontal",
                                            command=self.dummy_canvas.xview,
                                            **scrollbar_kwargs)
            self.h_scrollbar.grid(row=1, column=0, sticky="news")
            self.dummy_canvas.configure(xscrollcommand=self.h_scrollbar.set)

        # Bind to the mousewheel scrolling
        self.dummy_canvas.bind_all("<MouseWheel>", self.scrolling_windows,
                                   add=True)
        self.dummy_canvas.bind_all("<Button-4>", self.scrolling_linux, add=True)
        self.dummy_canvas.bind_all("<Button-5>", self.scrolling_linux, add=True)
        self.bind("<Configure>", self.scrollbar_scrolling, add=True)

        # Place `self` inside `dummy_canvas`
        self.dummy_canvas.create_window((0, 0), window=self, anchor="nw")
        # Place `dummy_canvas` inside `master_frame`
        self.dummy_canvas.grid(row=0, column=0, sticky="news")

        self.pack = self.master_frame.pack
        self.grid = self.master_frame.grid
        self.place = self.master_frame.place
        self.pack_forget = self.master_frame.pack_forget
        self.grid_forget = self.master_frame.grid_forget
        self.place_forget = self.master_frame.place_forget

    def scrolling_windows(self, event:tk.Event) -> None:
        assert event.delta != 0, "On Windows, `event.delta` should never be 0"
        y_steps = int(-event.delta/abs(event.delta)*self.scroll_speed)
        self.dummy_canvas.yview_scroll(y_steps, "units")

    def scrolling_linux(self, event:tk.Event) -> None:
        y_steps = self.scroll_speed
        if event.num == 4:
            y_steps *= -1
        self.dummy_canvas.yview_scroll(y_steps, "units")

    def scrollbar_scrolling(self, event:tk.Event) -> None:
        region = list(self.dummy_canvas.bbox("all"))
        region[2] = max(self.dummy_canvas.winfo_width(), region[2])
        region[3] = max(self.dummy_canvas.winfo_height(), region[3])
        self.dummy_canvas.configure(scrollregion=region)

    def resize(self, fit:str=None, height:int=None, width:int=None) -> None:
        """
        Resizes the frame to fit the widgets inside. You must either
        specify (the `fit`) or (the `height` or/and the `width`) parameter.
        Parameters:
            fit:str       `fit` can be either `FIT_WIDTH` or `FIT_HEIGHT`.
                          `FIT_WIDTH` makes sure that the frame's width can
                           fit all of the widgets. `FIT_HEIGHT` is simmilar
            height:int     specifies the height of the frame in pixels
            width:int      specifies the width of the frame in pixels
        To do:
            ALWAYS_FIT_WIDTH
            ALWAYS_FIT_HEIGHT
        """
        if height is not None:
            self.dummy_canvas.config(height=height)
        if width is not None:
            self.dummy_canvas.config(width=width)
        if fit == FIT_WIDTH:
            super().update()
            self.dummy_canvas.config(width=super().winfo_width())
        elif fit == FIT_HEIGHT:
            super().update()
            self.dummy_canvas.config(height=super().winfo_height())
        else:
            raise ValueError("Unknow value for the `fit` parameter.")
    fit = resize


class Calculator():

    def __init__(self):
        super().__init__()

        btn_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '0', 'Del']
        # create and position all buttons with a for-loop
        btn = []
        # Use custom generator to give us row/column positions
        for r, c, label in enumerate_row_column(btn_list, 3):
            # partial takes care of function and argument
            cmd = lambda x=label: self.click(x)
            # create the button
            cur = Button(numpad, text=label, width=5, height=4, command=cmd)
            # position the button
            cur.grid(row=r, column=c)
            btn.append(cur)

    def click(self, label):
        if label == 'Del':
            currentText = settingsList[currentSetting].get()
            settingsList[currentSetting].delete(0, END)
            settingsList[currentSetting].insert(0, currentText[:-1])
        else:
            currentText = settingsList[currentSetting].get()
            settingsList[currentSetting].delete(0, END)
            settingsList[currentSetting].insert(0, currentText + label)

class Calculator2():

    def __init__(self):
        super().__init__()

        btn_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '0', 'Del']
        # create and position all buttons with a for-loop
        btn = []
        # Use custom generator to give us row/column positions
        for r, c, label in enumerate_row_column(btn_list, 3):
            # partial takes care of function and argument
            cmd = lambda x=label: self.click(x)
            # create the button
            cur = Button(numpad2, text=label, width=5, height=4, command=cmd)
            # position the button
            cur.grid(row=r, column=c)
            btn.append(cur)

    def click(self, label):
        if label == 'Del':
            currentText = moveStepperInput.get()
            moveStepperInput.delete(0, END)
            moveStepperInput.insert(0, currentText[:-1])
        else:
            currentText = moveStepperInput.get()
            moveStepperInput.delete(0, END)
            moveStepperInput.insert(0, currentText + label)

class ResizingCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)

def submitForm():
    strFile = optVariable.get()
    # Print the selected value from Option (Combo Box)
    if (strFile !=''):
        print('Selected Value is : ' + strFile)

def write_slogan():
    print("Tkinter is easy to use!")

def hear():
    msg = usb.read_until() # read until a new line
    #mystring = msg.decode('ascii')  # decode n return
    mystring = json.loads(str(msg.decode("ascii")).strip())
    return mystring

def hearJson():
    msg = usb.read_until()# read until a new line
    mystring = json.loads(str(msg.decode("utf-8")).strip())

    if str(mystring["status"]).strip() != "done":
        errorBox.config(state=DISABLED, fg='white', bg='red')
    return mystring


def hearJsonf():

    #msg = usbf.read_until()# read until a new line
    #mystring = json.loads(str(msg.decode("Ascii")).strip())
    #return mystring

    while 1:
        if usbf.in_waiting > 0:

            # Read data out of the buffer until a carraige return / new line is found
            serialString = usbf.readline()

            # Print the contents of the serial data
            try:
                #print(serialString.decode("Ascii"))

                mystring = json.loads(str(serialString.decode("Ascii")).strip())
                #print(mystring)
                return mystring
            except:
                print("fail")
                pass

def hearJsonl():

    #msg = usbf.read_until()# read until a new line
    #mystring = json.loads(str(msg.decode("Ascii")).strip())
    #return mystring

    while 1:
        if usbl.in_waiting > 0:

            # Read data out of the buffer until a carraige return / new line is found
            serialString = usbl.readline()

            # Print the contents of the serial data
            try:
                #print(serialString.decode("Ascii"))

                mystring = json.loads(str(serialString.decode("Ascii")).strip())
                #print(mystring)
                return mystring
            except:
                print("fail")
                pass



def hearJsonf1():
    """while (True):
        if (usbf.in_waiting > 0):
            data_str = usbf.read_until()
            mystring = json.loads(str(data_str.decode("utf-8")).strip())
            return mystring

        # Put the rest of your code you want here

        time.sleep(0.01)
    """
    msg = usbf.read_until()# read until a new line
    mystring = json.loads(str(msg.decode("utf-8")).strip())
    return mystring

def callback(*args):
    res = c.execute("SELECT id,name FROM profili WHERE name LIKE ?", (str(monthchoosen.get()),)).fetchone()
    idProfil = int(res[0])
    if not idProfil:
        idProfil = 1

    res = c.execute("SELECT name,value FROM vars WHERE idProfil LIKE ?", (str(idProfil),)).fetchall()
    dbvars = dict(res)

    i=3
    for var in dbvars:
        settingsList[var].delete(0, END)
        settingsList[var].insert(0,dbvars[var])
        """tk.Label(canvas_tab2, text=var,font=text_font,anchor='w', width=25).grid(row=i,column=0)
        e1 = tk.Entry(canvas_tab2,font=text_font)
        e1.grid(row=i,column=1)
        e1.insert(0,dbvars[var])
        i+=1"""

def setStepperValue(*args):
    moveStepperInput.delete(0, END)
    moveStepperInput.insert(0,str(stepperList[int(stepperchoosen.get())]))

def saveSettings():
    res = c.execute("SELECT id,name FROM profili WHERE name LIKE ?", (str(monthchoosen.get()),)).fetchone()
    idProfil = int(res[0])
    if not idProfil:
        idProfil = 1

    for key in settingsList:
        print(key,idProfil,settingsList[key].get())
        c.execute("UPDATE vars SET value = ? WHERE name LIKE '"+key+"' AND idProfil = "+str(idProfil)+"", (float(settingsList[key].get()),))
        conn.commit()

def saveMachineSettings():

    c.execute("UPDATE vars SET value = ? WHERE name LIKE 'bias'", (float(bias.get()),))
    c.execute("UPDATE vars SET value = ? WHERE name LIKE 'bias2'", (float(bias2.get()),))
    conn.commit()

def addJob():

    addJobLength = float(jobLength.get())

    res = c.execute("SELECT id,name,loader FROM profili WHERE name LIKE ?", (str(jobProfile.get()),)).fetchone()
    idProfil = int(res[0])
    jobLoader = int(res[2])
    if not idProfil:
        idProfil = 1
        jobLoader = 0

    addJobQty = int(jobQty.get())

    c.execute("INSERT INTO job (length, qty,idProfile, loader, qtyD, done) VALUES ('"+str(addJobLength)+"','"+str(addJobQty)+"','"+str(idProfil)+"','"+str(jobLoader)+"','0','0')")
    conn.commit()

    initJobs()
    return True
    #res = c.execute("SELECT id,name FROM profili WHERE name LIKE ?", (str(monthchoosen.get()),)).fetchone()
    #idProfil = int(res[0])
    #if not idProfil:
    #    idProfil = 1

    #for key in settingsList:
    #    print(key, idProfil, settingsList[key].get())
    #    c.execute(
    #        "UPDATE vars SET value = ? WHERE name LIKE '" + key + "' AND idProfil = " + str(idProfil) + "",
    #        (float(settingsList[key].get()),))
    #    conn.commit()

def handle_focus(event):
    global currentSetting
    for k in settingsList:
        if event.widget == settingsList[k]:
            settingsList[k].config({"background": "#ffffcc"})
            currentSetting = k

def handle_focus_lost(event):
    global currentSetting
    for k in settingsList:
        if event.widget == settingsList[k]:
            settingsList[k].config({"background": "White"})
            currentSetting = k


def Simpletoggle():

    data = {
        "A": "spindle",
        "IDS": int(spindlechoosen.get()),
        "T": 1,
    }

    spindleList[int(spindlechoosen.get())] = 1;
    print(json.dumps(data).encode())
    usb.write(json.dumps(data).encode())
    hearv = hear()
    label.config(text=str(hearv))


def Simpletoggle2():
    data = {
        "A": "spindle",
        "IDS": int(spindlechoosen.get()),
        "T": 0,
    }

    spindleList[int(spindlechoosen.get())] = 0;
    print(json.dumps(data).encode())
    usb.write(json.dumps(data).encode())
    hearv = hear()
    label.config(text=str(hearv))

def toggleAllOff():
    global spindleList
    data = {
        "A": "spindleA",
        "T": 1,
    }

    spindleList = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
    print(json.dumps(data).encode())
    usb.write(json.dumps(data).encode())
    hearv = hear()
    label.config(text=str(hearv))

def toggleAllOn():
    global spindleList
    data = {
        "A": "spindleA",
        "T": 0,
    }

    spindleList = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1}
    print(json.dumps(data).encode())
    usb.write(json.dumps(data).encode())
    hearv = hear()
    label.config(text=str(hearv))

def changeTool(idTool, dir):

    action = (dir == "LEFT" and "CTL" or "CTR")

    data = {
        "A": action,
        "T": int(idTool),
    }

    usb.write(json.dumps(data).encode())
    hearv = hearJson()
    print(hearv)
    if str(hearv["status"]).strip() != "done":
        errorBox.config(state=DISABLED, fg='white', bg='red')
        return False
    else:
        return True

def ctrlDeleteJob(idJob):
    sql = 'DELETE FROM job WHERE id=?'
    cur = conn.cursor()
    #cur.execute(sql, (idJob,))
    #conn.commit()

    initJobs()

def ctrlConfirmJob(idJob):
    c.execute("UPDATE job SET done = 1 WHERE id = " + str(idJob) + "",)
    conn.commit()

    initJobs()

def runJobs():
    jobsRunning = True
    start_auto_thread()
    return True

def stopJobs():
    jobsRunning = False
    stop_auto_thread()
    return True

def initEmptyCombo():
    res = c.execute("SELECT name,value FROM vars WHERE idProfil LIKE ?", (str(1),)).fetchall()
    dbvars = dict(res)

    i = 3
    for var in dbvars:
        tk.Label(canvas_tab2, text=var, font=etext_font,anchor='w', width=25).grid(row=i, column=0)
        e1 = Entry(canvas_tab2, font=etext_font, width=10)
        e1.grid(row=i, column=1)
        settingsList[var] = e1
        settingsList[var].insert(0, 0)
        i += 1

def initJobs():
    for widget in vrtalkaDList.winfo_children():
        widget.destroy()

    res = c.execute("SELECT length,qty,idProfile,loader,qtyD,done,id FROM job WHERE done != 1 ORDER BY length ASC").fetchall()

    tk.Label(vrtalkaDList, text="Dolžina", font=etext_font, anchor='w', width=10).grid(row=2, column=0)
    tk.Label(vrtalkaDList, text="Profil", font=etext_font, anchor='w', width=25).grid(row=2, column=1)
    tk.Label(vrtalkaDList, text="Količina", font=etext_font, anchor='w', width=10).grid(row=2, column=2)
    tk.Label(vrtalkaDList, text="Ostane", font=etext_font, anchor='w', width=10).grid(row=2, column=3)
    tk.Label(vrtalkaDList, text="Zaključeno", font=etext_font, anchor='w', width=10).grid(row=2, column=4)
    tk.Label(vrtalkaDList, text="Potrdi", font=etext_font, anchor='w', width=5).grid(row=2, column=5)
    tk.Label(vrtalkaDList, text="Izbrisi", font=etext_font, anchor='w', width=5).grid(row=2, column=6)

    #imgConfirm = PhotoImage(file=r"confirm.png")
    #imgDelete = PhotoImage(file=r"delete.png")

    i = 3
    for row in res:

        rowLength = row[0]
        rowQty = row[1]

        res = c.execute("SELECT id,name,loader FROM profili WHERE id LIKE ?", (str(row[2]),)).fetchone()
        rowProfile = str(res[1])
        if not rowProfile:
            rowProfile = '/'

        rowQtyD = row[4]
        rowDone = row[5]
        tk.Label(vrtalkaDList, text=rowLength, font=etext_font,anchor='w', width=10).grid(row=i, column=0)
        tk.Label(vrtalkaDList, text=rowProfile, font=etext_font,anchor='w', width=25).grid(row=i, column=1)
        tk.Label(vrtalkaDList, text=rowQty, font=etext_font,anchor='w', width=10).grid(row=i, column=2)
        tk.Label(vrtalkaDList, text=rowQtyD, font=etext_font,anchor='w', width=10).grid(row=i, column=3)
        tk.Label(vrtalkaDList, text=rowDone, font=etext_font,anchor='w', width=10).grid(row=i, column=4)

        ctrlConfirm = Button(vrtalkaDList, text='Potrdi', command=lambda :ctrlConfirmJob(row[6]), bg='brown', fg='white',font=('Courier New', '18')).grid(column=5, row=i)
        ctrlDelete = Button(vrtalkaDList, text='Izbrisi', command=lambda :ctrlDeleteJob(row[6]), bg='brown', fg='white',font=('Courier New', '18')).grid(column=6, row=i)
        i += 1

def executeDrill():

    res = c.execute("SELECT id,name FROM profili WHERE name LIKE ?", (str(profilChooser.get()),)).fetchone()
    idProfil = int(res[0])
    if not idProfil:
        idProfil = 1

    res = c.execute("SELECT name,value FROM vars WHERE idProfil = ?", (str(idProfil),)).fetchall()
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
        "OL": int(dbvars["orodjeL"]),
        "OD": int(dbvars["orodjeD"]),
        "HL": dbvars["hodL"] * 160,
        "PHL": dbvars["pocasnejePredKoncemHodaL"]*160,
        "PHLH": dbvars["hitrostPredKoncemHodaL"],
        "HD": dbvars["hodD"] * 160,
        "PHD": dbvars["pocasnejePredKoncemHodaD"]*160,
        "PHDH": dbvars["hitrostPredKoncemHodaD"],
        "POL": dbvars["povratekL"] * 160,
        "POD": dbvars["povratekD"] * 160,
        "POVL": dbvars["povrtavanjeL"] * 160,
        "POVD": dbvars["povrtavanjeD"] * 160,
        "POVLI": int(dbvars["povrtavanjeLIzklop"]),
        "POVDI": int(dbvars["povrtavanjeDIzklop"]),
        "MAZD": int(dbvars["mazalkaProfil"])
    }

    usb.write(json.dumps(data).encode())
    hearv = hearJson()
    print(hearv)
    if str(hearv["status"]).strip() != "done":
        errorBox.config(state=DISABLED, fg='white', bg='red')
        return False
    else:
        return True

    #label.config(text=str(hearv))

def cut():
    res = c.execute("SELECT id,name FROM profili WHERE name LIKE ?", (str(profilChooser.get()),)).fetchone()
    idProfil = int(res[0])
    if not idProfil:
        idProfil = 1

    print(idProfil)

    res = c.execute("SELECT name,value FROM vars WHERE idProfil = ?", (str(idProfil),)).fetchall()
    dictionary = {}
    # dbvars = (Convert(res, dictionary))
    dbvars = dict(res)

    data = {
        "A": "cut",
        "MZ": dbvars["pozicijaZaga"] * 80,
        "PHZ": dbvars["pocasnejePredKoncemHodaZaga"] * 80,
        "PHZH": dbvars["hitrostPredKoncemHodaZaga"],
    }

    usb.write(json.dumps(data).encode())
    hearv = hearJson()
    """print(hearv)
    if str(hearv["status"]).strip() == "done":
        #cut.config(state=ACTIVE, bg='green')
    else:
        #cut.config(state=ACTIVE, bg='red')
    label.config(text=str(hearv))
"""

def runCycle1():
    moveFeeder("moveRev", int(1000))

def runCycle():

    global sensorToDrill
    global refExtension
    global currentCutLen
    global changingLen
    global currentProfileId
    global currentQty
    global currentSensorToDrill
    global manualLoading
    global disableDrill
    global balansRef
    global saw_width

    res = c.execute("SELECT id,name, loader FROM profili WHERE name LIKE ?", (str(profilChooser.get()),)).fetchone()
    idProfil = int(res[0])
    loadingBay = int(res[2])
    if not idProfil:
        idProfil = 1
        loadingBay = 0

    # setup bias biff based on db values
    tmpRes = c.execute("SELECT id,name,value FROM vars WHERE name = 'bias'").fetchone()
    tmpBias1 = float(tmpRes[2])
    tmpRes = c.execute("SELECT id,name,value FROM vars WHERE name = 'bias2'").fetchone()
    tmpBias2 = float(tmpRes[2])

    biasDiff = (tmpBias1 - tmpBias2)

    toolSetup = False
    if currentProfileId is None:
        currentProfileId = idProfil
        toolSetup = True
    elif currentProfileId != idProfil:
        currentProfileId = idProfil
        toolSetup = True

    if toolSetup:
        res = c.execute("SELECT name,value FROM vars WHERE idProfil = ?", (str(idProfil),)).fetchall()
        dbvars = dict(res)
        if float(dbvars['sensorToDrill']) == 0.0:
            currentSensorToDrill = sensorToDrill
        else:
            currentSensorToDrill = float(dbvars['sensorToDrill'])
        currentSensorToDrill = sensorToDrill


        changeTool(int(dbvars["orodjeL"]), 'LEFT')
        changeTool(int(dbvars["orodjeD"]), 'RIGHT')

        # reset bias value if wrong tool
        if int(dbvars["orodjeL"]) == 1:
            biasDiff = 0 

    if manualLoading:
        while 1:

            print("Run cycle ročno")
            cut = float(runLength.get().replace(',', '.'))
            #add_log(cut)
            print(str(cut))

        
            # if currentCutLen == 0:
            #    currentCutLen = cut

            # if currentCutLen != cut and 0:
            #    changeLength()
            #    currentCutLen = cut

            print("Rev move to load profile")
            tmpStatus = moveFeeder("moveRev", float(
                runLength.get().replace(',', '.')) + saw_width + refExtension, 1, 1)

            print("Extend extension")
            tmpStatus = extensionE()

            #print("Fold extension")
            #tmpStatus = extensionF()

            # raspberry should ping loader if is loaded and retry after a sec. eg. waitForProfile() func

            print("Load profile")
            add_log("Load profile")
            tmpStatus = waitForProfile()
            while tmpStatus != "done":
                # wait for profile
                if changingLen == True:
                    resetLoader()
                    print("Drop cycle")
                    runCyc.config(state=NORMAL, bg='green')
                    return

                print("Waiting for profile")
                time.sleep(1)
                tmpStatus = waitForProfile()

            # tmpStatus = unloadProfile()
            print("Profile loaded")
            #tmpStatus = moveFeeder("moveRev",
            #                       float(runLength.get().replace(',', '.')) + currentSensorToDrill + refExtension, 1, 1)

            #print("Wait for loading sensor")
            #tmpStatus = waitForProfile()
            #while tmpStatus != "done":
                # wait for profile
            #    if changingLen == True:
            #        print("Drop cycle")
            #        runCyc.config(state=NORMAL, bg='green')
            #        return

            #    print("Waiting for profile")
            #    time.sleep(1)
            #    tmpStatus = waitForProfile()

            fromStart = 0.0;
            nbrOfHoles = int(cut // 120)
            rem = cut % 120
            fromStart = refExtension + (120 - rem)
            if rem == 0:
                nbrOfHoles -= 1
            else:
                tmpCut = (int(cut // 120) + 1) * 120
                rem = (tmpCut - cut) / 2
                fromStart = refExtension + (120 - rem)

            fromStart += saw_width
            fromStart += sensorToDrill
            fromStart += biasDiff

            add_log("Št. lukenj: "+str(nbrOfHoles))
            print("Prva ročno: " + str(fromStart))
            tmpStatus = moveFeeder("moveFwd", float(fromStart))

            print("Drill prva")
            if not disableDrill:
                drillRes = executeDrill()
                if not drillRes:
                    print("Drill error")
                    return

            if changingLen == True:
                print("Drop cycle")
                runCyc.config(state=NORMAL, bg='green')
                return

            moveTo = fromStart
            for x in range(1, nbrOfHoles):

                if changingLen == True:
                    print("Drop cycle")
                    runCyc.config(state=NORMAL, bg='green')
                    return

                moveTo += 120
                print(str(x) + " : " + str(moveTo))
                moveFeeder("moveFwd", 120)
                print("Drill " + str(x) + ".")
                if not disableDrill:
                    drillRes = executeDrill()
                    if not drillRes:
                        print("Drill error")
                        return

    else:
        while currentQty > 0:

            print("Run cycle")
            cut = float(runLength.get().replace(',', '.'))
            print(cut)
            # if currentCutLen == 0:
            #    currentCutLen = cut

            # if currentCutLen != cut and 0:
            #    changeLength()
            #    currentCutLen = cut

            print("Rev move to load profile")
            tmpStatus = retractLoader()

            tmpEL = extensionLength
            if cut < 250:
                tmpEL = 0

            tmpStatus = moveFeeder("moveRev", float(
                runLength.get().replace(',', '.')) + saw_width + refExtension - tmpEL, 1, 1)

            print("Fold extension in extended")
            tmpStatus = extensionF()

            # raspberry should ping loader if is loaded and retry after a sec. eg. waitForProfile() func

            print("Load profile")
            tmpStatus = loadProfile(loadingBay, 1 if cut < 250 else 0)
            tmpStatus = waitForProfile()
            while tmpStatus != "done":
                # wait for profile
                if changingLen == True:
                    resetLoader()
                    print("Drop cycle")
                    runCyc.config(state=NORMAL, bg='green')
                    return

                print("Waiting for profile")
                time.sleep(1)
                tmpStatus = waitForProfile()

            # tmpStatus = unloadProfile()
            print("Profile loaded")
            tmpStatus = retractLoader()
            tmpStatus = moveFeeder("moveRev",
                                   float(runLength.get().replace(',', '.')) + saw_width + refExtension, 1, 1)

            print("Extend extension")
            tmpStatus = extensionE()

            print("Load profile")
            tmpStatus = waitForProfile()
            while tmpStatus != "done":
                # wait for profile
                if changingLen == True:
                    resetLoader()
                    print("Drop cycle")
                    runCyc.config(state=NORMAL, bg='green')
                    return

                print("Waiting for profile")
                time.sleep(1)
                tmpStatus = waitForProfile()

            nbrOfHoles = int(cut // 120)
            rem = cut % 120
            fromStart = refExtension + (120 - rem)
            if rem == 0:
                nbrOfHoles -= 1
            else:
                tmpCut = (int(cut // 120) + 1) * 120
                rem = (tmpCut - cut) / 2
                fromStart = refExtension + (120 - rem)

            fromStart += saw_width
            fromStart += sensorToDrill
            fromStart += biasDiff

            print("Prva: " + str(fromStart))
            tmpStatus = moveFeeder("moveFwdF", fromStart)

            print("Drill prva")
            if not disableDrill:
                drillRes = executeDrill()
                if not drillRes:
                    print("Drill error")
                    return

            if changingLen == True:
                resetLoader()
                print("Drop cycle")
                runCyc.config(state=NORMAL, bg='green')
                return

            moveTo = fromStart
            for x in range(1, nbrOfHoles):

                if changingLen == True:
                    resetLoader()
                    print("Drop cycle")
                    runCyc.config(state=NORMAL, bg='green')
                    return

                moveTo += 120
                print(str(x) + " : " + str(moveTo))
                moveFeeder("moveFwd", 120)
                print("Drill " + str(x) + ".")
                if not disableDrill:
                    drillRes = executeDrill()
                    if not drillRes:
                        print("Drill error")
                        return
            currentQty = currentQty - 1
            runQtyR.config(text=str(currentQtyLabel-currentQty)+' / ' + str(currentQtyLabel))
        if currentQty == 0:
            runCyc.config(state=ACTIVE, bg='green')
            changeLen.config(state=ACTIVE, bg='green')

def runAuto():

    global sensorToDrill
    global refExtension
    global currentCutLen
    global changingLen
    global currentProfileId
    global currentQty
    global currentSensorToDrill
    global manualLoading
    global disableDrill

    res = c.execute("SELECT id,length, qty, idProfile, loader, qtyD, done FROM job WHERE done = 0 ORDER BY length ASC").fetchone()
    idProfil = int(res[3])
    loadingBay = int(res[4])
    currJobLength = float(res[1])
    currJobQty = int(res[2])

    toolSetup = False
    if currentProfileId is None:
        currentProfileId = idProfil
        toolSetup = True
    elif currentProfileId != idProfil:
        currentProfileId = idProfil
        toolSetup = True

    if toolSetup:
        res = c.execute("SELECT name,value FROM vars WHERE idProfil = ?", (str(idProfil),)).fetchall()
        dbvars = dict(res)
        if float(dbvars['sensorToDrill']) == 0.0:
            currentSensorToDrill = sensorToDrill
        else:
            currentSensorToDrill = float(dbvars['sensorToDrill'])
        currentSensorToDrill = sensorToDrill

        changeTool(int(dbvars["orodjeL"]), 'LEFT')
        changeTool(int(dbvars["orodjeD"]), 'RIGHT')


    while currJobQty > 0:

        print("Run cycle")
        cut = currJobLength
        print(cut)
        # if currentCutLen == 0:
        #    currentCutLen = cut

        # if currentCutLen != cut and 0:
        #    changeLength()
        #    currentCutLen = cut

        print("Rev move to load profile")
        tmpStatus = retractLoader()

        tmpEL = extensionLength
        if cut < 250:
            tmpEL = 0
        
        tmpStatus = moveFeeder("moveRev", float(
            runLength.get().replace(',', '.')) + currentSensorToDrill + refExtension - tmpEL , 1, 1)

        print("Fold extension in extended")
        tmpStatus = extensionF()

        # raspberry should ping loader if is loaded and retry after a sec. eg. waitForProfile() func

        print("Load profile")
        tmpStatus = loadProfile(loadingBay, 1 if cut < 250 else 0)
        tmpStatus = waitForProfile()
        while tmpStatus != "done":
            # wait for profile
            if stop_auto_thread == True:
                resetLoader()
                print("Drop cycle")
                runCyc.config(state=NORMAL, bg='green')
                return

            print("Waiting for profile")
            time.sleep(1)
            tmpStatus = waitForProfile()

        # tmpStatus = unloadProfile()
        print("Profile loaded")
        tmpStatus = retractLoader()
        tmpStatus = moveFeeder("moveRev",
                               float(runLength.get().replace(',', '.')) + currentSensorToDrill + refExtension, 1, 1)

        print("Extend extension")
        tmpStatus = extensionE()

        print("Load profile")
        tmpStatus = waitForProfile()
        while tmpStatus != "done":
            # wait for profile
            if stop_auto_thread == True:
                resetLoader()
                print("Drop cycle")
                runCyc.config(state=NORMAL, bg='green')
                return

            print("Waiting for profile")
            time.sleep(1)
            tmpStatus = waitForProfile()

        nbrOfHoles = int(cut // 120)
        rem = cut % 120
        fromStart = refExtension + (120 - rem)
        if rem == 0:
            nbrOfHoles -= 1
        else:
            tmpCut = (int(cut // 120) + 1) * 120
            rem = (tmpCut - cut) / 2
            fromStart = refExtension + (120 - rem)

        print("Prva: " + str(fromStart))
        tmpStatus = moveFeeder("moveFwdF", int(fromStart))

        print("Drill prva")
        if not disableDrill:
            drillRes = executeDrill()
            if not drillRes:
                print("Drill error")
                return

        if stop_auto_thread == True:
            resetLoader()
            print("Drop cycle")
            runCyc.config(state=NORMAL, bg='green')
            return

        moveTo = fromStart
        for x in range(1, nbrOfHoles):

            if stop_auto_thread == True:
                resetLoader()
                print("Drop cycle")
                runCyc.config(state=NORMAL, bg='green')
                return

            moveTo += 120
            print(str(x) + " : " + str(moveTo))
            moveFeeder("moveFwd", 120)
            print("Drill " + str(x) + ".")
            if not disableDrill:
                drillRes = executeDrill()
                if not drillRes:
                    print("Drill error")
                    return
        currJobQty = currJobQty - 1



# abs = 1 => move to absolute position
# abs = 0 => relative move
def moveFeeder(dir, step, abs = 0, firstMove = 0):
    res = c.execute("SELECT id,name FROM profili WHERE name LIKE ?", (str(profilChooser.get()),)).fetchone()
    idProfil = int(res[0])
    if not idProfil:
        idProfil = 1

    runCyc.config(state=DISABLED, fg='white', bg='#e69225')

    #44.44
    # 0.005 koraka cca 0.5mm
    # 44.385 12.12.2023
    # zobata letev 36.5785
    data = {
        "A": str(dir),
        "M": int((float(step) * 36.5785)),
        "M2": abs,
        "P": idProfil,
        "F": firstMove
    }

    usbf.write(json.dumps(data).encode())
    hearv = hearJsonf()
    #print(hearv)
    if str(hearv["status"]).strip() == "waitingForProfile":
        runCyc.config(state=ACTIVE, bg='green')
        #print("Enabled")
    """else:
        #cut.config(state=ACTIVE, bg='red')
    label.config(text=str(hearv))
"""
    return hearv["status"]

def resetLoader():
    runCyc.config(state=DISABLED, fg='white', bg='#e69225')

    data = {
        "A": "resetLoader"
    }

    usbl.write(json.dumps(data).encode())
    #hearv = hearJsonl()
    #print(hearv)
    #if str(hearv["status"]).strip() == "done":
    runCyc.config(state=ACTIVE, bg='green')

    #return hearv["status"]
    return True

def retractLoader():
    runCyc.config(state=DISABLED, fg='white', bg='#e69225')

    data = {
        "A": "retractLoader"
    }

    usbl.write(json.dumps(data).encode())
    hearv = hearJsonl()
    #print(hearv)
    if str(hearv["status"]).strip() == "done":
        runCyc.config(state=ACTIVE, bg='green')

    return hearv["status"]

def extensionE():
    runCyc.config(state=DISABLED, fg='white', bg='#e69225')

    data = {
        "A": "extensionE"
    }

    usbl.write(json.dumps(data).encode())
    hearv = hearJsonl()
    #print(hearv)
    if str(hearv["status"]).strip() == "done":
        runCyc.config(state=ACTIVE, bg='green')

    return hearv["status"]

def extensionF():
    runCyc.config(state=DISABLED, fg='white', bg='#e69225')

    data = {
        "A": "extensionF"
    }

    usbl.write(json.dumps(data).encode())
    hearv = hearJsonl()

    if str(hearv["status"]).strip() == "done":
        runCyc.config(state=ACTIVE, bg='green')

    return hearv["status"]

def loadProfile(idBay = 0, singleLoader = 0):
    runCyc.config(state=DISABLED, fg='white', bg='#e69225')

    data = {
        "A": "load",
        "B": idBay,
        "L": singleLoader
    }
    print(data)
    usbl.write(json.dumps(data).encode())
    hearv = hearJsonl()

    if str(hearv["status"]).strip() == "done":
        runCyc.config(state=ACTIVE, bg='green')

    return hearv["status"]

def unloadProfile():
    runCyc.config(state=DISABLED, fg='white', bg='#e69225')

    data = {
        "A": "unload"
    }

    usbl.write(json.dumps(data).encode())
    hearv = hearJsonl()

    if str(hearv["status"]).strip() == "done":
        runCyc.config(state=ACTIVE, bg='green')

    return hearv["status"]


def waitForProfile():
    res = c.execute("SELECT id,name FROM profili WHERE name LIKE ?", (str(profilChooser.get()),)).fetchone()
    idProfil = int(res[0])
    if not idProfil:
        idProfil = 1

    data = {
        "A": "waitForProfile",
        "P": idProfil
    }

    usbf.write(json.dumps(data).encode())
    hearv = hearJsonf()
    print(hearv)
    return hearv["status"]


def start_thread():
    # Assign global variable and initialize value
    global changingLen
    global cycleThread
    global currentQty
    changingLen = False

    currentQty = int(runQty.get())
    currentQtyLabel = int(runQty.get())
    runQtyR.config(text='0 / '+str(currentQtyLabel))
    # Create and launch a thread
    cycleThread = Thread(target=runCycle)
    cycleThread.start()

def stop_thread():
    # Assign global variable and set value to stop
    global cycleThread
    global changingLen
    global currentQty
    currentQty = 0
    currentQtyLabel = 0
    runQtyR.config(text='0 / 0')
    changingLen = True
    #changeLength()
    #cycleThread.join()


def start_auto_thread():
    # Assign global variable and initialize value
    global changingLen
    global cycleAutoThread
    stop_auto_thread = False

    # Create and launch a thread
    cycleAutoThread = Thread(target=runAuto)
    cycleAutoThread.start()

def stop_auto_thread():
    # Assign global variable and set value to stop
    global cycleAutoThread
    global stop_auto_thread

    stop_auto_thread = True


def changeLength():
    data = {
        "A": "changeLength",
    }

    usbf.write(json.dumps(data).encode())
    hearv = hearJsonf()
    print(hearv)
    """if str(hearv["status"]).strip() == "done":
        #cut.config(state=ACTIVE, bg='green')
    else:
        #cut.config(state=ACTIVE, bg='red')
    label.config(text=str(hearv))
"""


def homeFeeder():

    #homingf.config(state=DISABLED, fg='white', bg='#e69225')

    data = {
        "A": "home"
    }

    usbf.write(json.dumps(data).encode())
    hearv = hearJsonf()
    #if str(hearv["status"]).strip() == "done":
        #homingf.config(state=ACTIVE, bg='green')
    #else:
        #homingf.config(state=ACTIVE, bg='red')

def refFeeder(dis):

    #homingf.config(state=DISABLED, fg='white', bg='#e69225')

    data = {
        "A": "setRef",
        "M": int((float(dis) * 36.5785))
    }

    usbf.write(json.dumps(data).encode())
    hearv = hearJsonf()
    #if str(hearv["status"]).strip() == "done":
        #homingf.config(state=ACTIVE, bg='green')
    #else:
        #homingf.config(state=ACTIVE, bg='red')


def changeLen():
    changeLen = True

def home():

    global stepperList
    #homingd.config(state=DISABLED,fg='white',bg='#e69225')
    data = {
        "action": "home",
    }

    usb.write(json.dumps(data).encode())
    hearv = hearJson()
    print(hearv)
    if str(hearv["status"]).strip() == "done":
        #homingd.config(state=ACTIVE, bg='green')
        stepperList = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
    #else:
        #homingd.config(state=ACTIVE, bg='red')
    #label.config(text=str(hearv))

def homeAll():
    global feederRef

    home()
    #homeFeeder()

    res = c.execute("SELECT id,name,value FROM vars WHERE name = 'bias'").fetchone()
    balansRef = float(res[2])

    refFeeder(balansRef)
    runCyc.config(state=ACTIVE, bg='green')
    changeLen.config(state=ACTIVE, bg='green')

def moveStepper():

    global stepperList

    stepRatio = 160
    if int(stepperchoosen.get()) == 7:
        stepRatio = 80

    data = {
        "A": "moveS",
        "IDS": int(stepperchoosen.get()),
        "MS": float(moveStepperInput.get()) * stepRatio,
    }

    stepperList[int(stepperchoosen.get())] = float(moveStepperInput.get())

    usb.write(json.dumps(data).encode())
    hearv = hearJson()
    if str(hearv["status"]).strip() == "done":
        listInt = 1
        for stepperData in hearv["data"]:
            stepperList[listInt] = float(stepperData) / stepRatio
            listInt+=1

    label.config(text=str(hearv["status"]))

def nbrOfHoles(sv):
    if runLength.get():
        nbrOfHoles = int(float(runLength.get()) // 120)
        rem = float(runLength.get()) % 120
        if rem == 0:
            nbrOfHoles -= 1
    else:
        nbrOfHoles = 0
    runLengthNOH.config(text=str(nbrOfHoles))


def manualLoad():
    global manualLoading
    # Determine is on or off
    if manualLoading:
        mlButton.config(image=off)
        manualLoading = False
    else:
        mlButton.config(image=on)
        manualLoading = True

def add_log(log):
    output.insert("end", log + "\n")
    output.see("end")
    #output.after(1000, add_timestamp)

main = tk.Tk()
main.geometry("1920x1080")
app=FullScreenApp(main)

text_font = ('Arial', '26')
etext_font = ('Arial', '18')

s = ttk.Style()
s.configure('TNotebook.Tab', font=('Arial' ,'18'))
s.configure('TNotebook.Tab', padding=(30 ,10))

notebook = ttk.Notebook(main, width=1900, height=1000)

# create frames
tab1 = ttk.Frame(notebook, width=1900, height=950)
tab2 = ttk.Frame(notebook, width=1900, height=950)
tab3 = ttk.Frame(notebook, width=1900, height=950)
tab4 = ttk.Frame(notebook, width=1900, height=950)

# add frames to notebook

notebook.add(tab1, text='Vrtalka')
notebook.add(tab2, text='Nastavitve')
notebook.add(tab3, text='Ročno upravljanje')
notebook.add(tab4, text='Nastavitve stroja')
notebook.pack(side=TOP)

vrtalkaL = ttk.Frame(tab1, width=600, height=950)
vrtalkaL.pack(expand=True, anchor='nw', side=LEFT,padx=60, pady=40)

vrtalkaD = ttk.Frame(tab1, width=1300, height=200)
vrtalkaD.pack(expand=True, anchor='nw', side=TOP, pady=40)

vrtalkaDList = ScrollableFrame(tab1, height=750, width=1300, hscroll=False, vscroll=True)
vrtalkaDList.pack(side=BOTTOM, expand=True, anchor='nw')

runJobs = Button(vrtalkaD, text='Zaženi', command=runJobs,bg='green',fg='white', font=('Courier New', '32')).grid(column=0, columnspan=3, row=0, pady=30)
stobJobs = Button(vrtalkaD, text='Stop', command=stopJobs,bg='red',fg='white', font=('Courier New', '32')).grid(column=1, columnspan=4, row=0, pady=30)


jobLength = Entry(vrtalkaD, font=text_font, width=10)
jobLength.grid(row=1, column=0,columnspan=2,sticky=W+E)
jobLength.insert(0, 0.0)

n = tk.StringVar()
n.trace("w", callback)
res = c.execute("SELECT id,name FROM profili").fetchall()
profilList = dict(res)
jobProfile = ttk.Combobox(vrtalkaD, width=25,textvariable=n,font=text_font, style='my.TCombobox')
# Adding combobox drop down list
jobProfile['values'] = list(profilList.values())
jobProfile.grid(column=2,columnspan=2, row=1)
main.option_add('*TCombobox*Listbox.font', text_font)

jobQty = Entry(vrtalkaD, font=text_font, width=5)
jobQty.grid(row=1, column=4,columnspan=2,sticky=W+E)
jobQty.insert(0, 0)


addJob = Button(vrtalkaD, text='Dodaj', command=addJob,bg='brown',fg='white', font=('Courier New', '24')).grid(column=6, row=1)
initJobs()


canvas_tab2 = ScrollableFrame(tab2, height=950, width=900, hscroll=False, vscroll=True)
canvas_tab2.pack(side=LEFT, expand=True, anchor='w')

numpad = ttk.Frame(tab2, width=900, height=950)
numpad.pack(expand=True, anchor='nw', side=LEFT,padx=60, pady=40)


#canvas_tab3 = ScrollableFrame(tab3, height=500, width=690, hscroll=False, vscroll=True)
canvas_tab3 = ttk.Frame(tab3, height=950, width=900)
#canvas_tab3.pack(side=LEFT, expand=True, anchor='nw')
canvas_tab3.grid(column=0, row=0)

tool_tab3 = ttk.Frame(tab3, height=50, width=300)
#tool_tab3.pack(side=LEFT, expand=False, anchor='w')
tool_tab3.grid(column=0, row=1)

canvas_tab4 = ttk.Frame(tab4, height=950, width=900)
#canvas_tab3.pack(side=LEFT, expand=True, anchor='nw')
canvas_tab4.grid(column=0, row=0)


numpad2 = ttk.Frame(tab3, width=900, height=950,borderwidth=1)
#numpad2.pack(expand=True, anchor='e')
numpad2.grid(column=1, row=0,sticky="ew",padx=40, pady=40)

button = tk.Button(vrtalkaL,
                   text="Zapri",
                   font=text_font,
                   fg="red",
                   command=quit).grid(column=0,
                               row=0,
                               padx=30,
                               pady=30)

tk.Label(vrtalkaL, text='     \n   ').grid(column=0,row=2)
tk.Label(vrtalkaL, text='     \n   ').grid(column=0,row=3)


#cut = tk.Button(tab1,text="Žaga",font=text_font,bg="green",command=cut)\
#    .grid(column=2,columnspan=2,sticky=W+E,row=5,padx=30,pady=30)

sv = StringVar()
sv.trace("w", lambda name, index, mode, sv=sv: nbrOfHoles(sv))
runLengthNOHL = Label(vrtalkaL, text='Št. lukenj:',font=text_font)
runLengthNOHL.grid(row=7, column=0,sticky=W+E)
runLengthNOH = Label(vrtalkaL, text='',font=text_font)
runLengthNOH.grid(row=7, column=1,sticky=W+E)


runLengthL = Label(vrtalkaL, text='Dolžina:',font=text_font)
runLengthL.grid(row=6, column=0,sticky=W+E)
runLength = Entry(vrtalkaL, font=etext_font, width=10,textvariable=sv)
runLength.grid(row=6, column=1,columnspan=2,sticky=W+E)
runLength.insert(0, 0.0)


runQtyL = Label(vrtalkaL, text='Količina:',font=text_font)
runQtyL.grid(row=8, column=0,sticky=W+E)
runQty = Entry(vrtalkaL, font=etext_font, width=10)
runQty.grid(row=8, column=1,columnspan=2,sticky=W+E)
runQty.insert(0, 0)
runQtyR = Label(vrtalkaL, text='0 / 0',font=text_font)
runQtyR.grid(row=8, column=2,sticky=W+E)

runCyc = tk.Button(vrtalkaL,text="Cikel",font=text_font,bg="green",command=start_thread)
runCyc.grid(column=0,columnspan=2,sticky=W+E,row=9,padx=30,pady=30)
runCyc.config(state=DISABLED, fg='white', bg='red')
changeLen = tk.Button(vrtalkaL,text="Ustavi cikel",font=text_font,bg="green",command=stop_thread)
changeLen.grid(column=1,columnspan=2,sticky=W+E,row=9,padx=30,pady=30)
changeLen.config(state=DISABLED, fg='white', bg='red')

errorBox = tk.Button(vrtalkaL,text="",font=text_font,bg="green",)
errorBox.grid(column=0,columnspan=4,sticky=W+E,row=10,padx=30, pady=30)

mlButtonLabel = Label(vrtalkaL, text = "Ročno nalaganje:", fg = "green", font = ("Helvetica", 24))
mlButtonLabel.grid(column=0,columnspan=4,sticky=W,row=11,padx=5, pady=30)

output = tk.Text(vrtalkaL, height=6, width=40, fg = "green", font = ("Helvetica", 24))
output.grid(column=0,columnspan=4,sticky=W,row=12,padx=5, pady=30)

on = PhotoImage(file = "/home/pi/profilapp/on.png")
off = PhotoImage(file = "/home/pi/profilapp/off.png")
mlButton = Button(vrtalkaL, image = off, bd = 0,command = manualLoad)
mlButton.grid(column=2,columnspan=1,sticky=W,row=11,padx=10, pady=30)


#homingd = tk.Button(vrtalkaL,text="Homing d",font=text_font,command=home)
#homingd.grid(column=2,row=9,padx=30,pady=30)

#homingf = tk.Button(vrtalkaL,text="Homing F",font=text_font,command=homeFeeder)
#homingf.grid(column=3,row=9,padx=30,pady=30)


homingA = tk.Button(vrtalkaL,text="Homing",font=text_font,command=homeAll)
homingA.grid(column=2,row=0,padx=30,pady=30)

res = c.execute("SELECT id,name FROM profili").fetchall()
profilList = dict(res)

profilChooser = ttk.Combobox(vrtalkaL, width=25,font=text_font, style='my.TCombobox')
# Adding combobox drop down list
profilChooser['values'] = list(profilList.values())
profilChooser.grid(column=0, row=2, columnspan=3)

style = ttk.Style() #If you dont have a class, put your root in the()
style.configure('TCombobox', arrowsize=50)

n = tk.StringVar()
n.trace("w", callback)


monthchoosen = ttk.Combobox(canvas_tab2, width=25,textvariable=n,font=text_font, style='my.TCombobox')
# Adding combobox drop down list
monthchoosen['values'] = list(profilList.values())
monthchoosen.grid(column=0, row=0)
main.option_add('*TCombobox*Listbox.font', text_font)
initEmptyCombo()

saveSett = Button(canvas_tab2, text='Shrani', command=saveSettings,bg='brown',fg='white', font=('Courier New', '24')).grid(column=1, row=0)

n1 = tk.StringVar()
n1.trace("w", setStepperValue)

tk.Label(canvas_tab3, text="Izberi stepper: ", font=text_font,anchor='w', width=15).grid(column=0, row=0,pady=(15,0))
stepperchoosen = ttk.Combobox(canvas_tab3, width=5,textvariable=n1,font=('Arial', '30'))
# Adding combobox drop down list
stepperchoosen['values'] = [1,2,3,4,5,6,7]
stepperchoosen.grid(column=1, row=0)
main.option_add('*TCombobox*Listbox.font', text_font)

tk.Label(canvas_tab3, text="Premakni za: ", font=text_font,anchor='w', width=15).grid(column=0, row=2,pady=(15,0))
moveStepperInput = Entry(canvas_tab3, font=text_font, width=10)
moveStepperInput.grid(column=1, row=2)

stepperButton = Button(canvas_tab3, text='Premakni stepper', command=moveStepper, width=20,bg='brown',fg='white',font=('Arial', '20')).grid(column=0, row=3)
#tk.Label(canvas_tab3, text='     \n   ').grid(column=0,row=4)

tk.Label(canvas_tab3, text="Izberi spindle: ", font=text_font,anchor='w', width=15).grid(column=0, row=5,pady=(15,0))
spindlechoosen = ttk.Combobox(canvas_tab3, width=5,textvariable=n,font=('Arial', '30'))
# Adding combobox drop down list
spindlechoosen['values'] = [1,2,3,4,5,6,7]
spindlechoosen.grid(column=1, row=5)

tk.Label(canvas_tab3, text='     \n   ').grid(column=0,row=6)

toggle_button = Button(canvas_tab3,text="OFF", width=10, command=Simpletoggle, bg='brown',fg='white',font=('Arial', '20')).grid(column=0, row=7)
toggle_button2 = Button(canvas_tab3,text="ON", width=10, command=Simpletoggle2, bg='green',font=('Arial', '20')).grid(column=1, row=7)

tk.Label(canvas_tab3, text='     \n   ').grid(column=0,row=8)

toggle_button3 = Button(canvas_tab3,text="OFF ALL", width=10, command=toggleAllOff, bg='brown',fg='white',font=('Arial', '20')).grid(column=0, row=9)
toggle_button4 = Button(canvas_tab3,text="ON ALL", width=10, command=toggleAllOn, bg='green',font=('Arial', '20')).grid(column=1, row=9)
tk.Label(canvas_tab3, text='     \n   ').grid(column=0,row=10)

drill = tk.Button(canvas_tab3,text="Vrtaj",font=text_font,bg="green",command=executeDrill)\
    .grid(column=0,columnspan=2,sticky=W+E,row=10,padx=30,pady=30)



toolButton1 = Button(tool_tab3,text="T1", width=10, command=lambda :changeTool(1,'LEFT'), bg='green',font=('Arial', '20')).grid(column=0, row=0)
toolButton2 = Button(tool_tab3,text="T3", width=10, command=lambda :changeTool(3,'LEFT'), bg='green',font=('Arial', '20')).grid(column=1, row=0)
toolButton3 = Button(tool_tab3,text="T2", width=10, command=lambda :changeTool(2,'RIGHT'), bg='green',font=('Arial', '20')).grid(column=2, row=0)
toolButton4 = Button(tool_tab3,text="T4", width=10, command=lambda :changeTool(4,'RIGHT'), bg='green',font=('Arial', '20')).grid(column=3, row=0)

bias = Label(canvas_tab4, text='Bias sveder 4,2mm:',font=text_font)
bias.grid(row=1, column=0,sticky=W+E)
bias = Entry(canvas_tab4, font=etext_font, width=10)
bias.grid(row=1, column=1,columnspan=2,sticky=W+E)
res = c.execute("SELECT id,name,value FROM vars WHERE name = 'bias'").fetchone()
bias.insert(0, float(res[2]))

bias2 = Label(canvas_tab4, text='Bias sveder 5mm:',font=text_font)
bias2.grid(row=2, column=0,sticky=W+E)
bias2 = Entry(canvas_tab4, font=etext_font, width=10)
bias2.grid(row=2, column=1,columnspan=2,sticky=W+E)
res = c.execute("SELECT id,name,value FROM vars WHERE name = 'bias2'").fetchone()
bias2.insert(0, float(res[2]))


saveSett = Button(canvas_tab4, text='Shrani nastavitve', command=saveMachineSettings,bg='brown',fg='white', font=('Courier New', '24')).grid(column=1, row=0)


Calculator()
Calculator2()
main.bind("<FocusIn>", handle_focus)
main.bind("<FocusOut>", handle_focus_lost)

main.mainloop()

