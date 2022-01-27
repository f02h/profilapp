import tkinter as tk
import serial
import json
import sqlite3
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import os
from tkinter import simpledialog




USB_PORT = "/dev/ttyACM0"
usb = serial.Serial(USB_PORT, 115200)
#usb = 0
path = os.path.dirname(os.path.abspath(__file__))
db = os.path.join(path, 'todo.db')

conn = sqlite3.connect(db)
c = conn.cursor()

settingsList = dict()
currentSetting = None

def enumerate_row_column(iterable, num_cols):
    for idx, item in enumerate(iterable):
        row = idx // num_cols
        col = idx % num_cols
        yield row, col, item

"""
class NumpadEntry(Entry):
    def __init__(self, parent=None, **kw):
        Entry.__init__(self, parent, **kw)
        self.bind('<FocusIn>', self.numpadEntry)
        self.bind('<FocusOut>', self.numpadExit)
        self.edited = False

    def numpadEntry(self, event):
        if self.edited == False:
            print("You Clicked on me")
            self['bg'] = '#ffffcc'
            self.edited = True
            new = numPad(self)
        else:
            self.edited = False

    def numpadExit(self, event):
        self['bg'] = '#ffffff'


class numPad(simpledialog.Dialog):
    def __init__(self, master=None, textVariable=None):
        self.top = Toplevel(master=master)
        self.top.protocol("WM_DELETE_WINDOW", self.ok)
        self.createWidgets()
        self.master = master

    def createWidgets(self):
        btn_list = ['7', '8', '9', '4', '5', '6', '1', '2', '3', '0', 'Close', 'Del']
        # create and position all buttons with a for-loop
        btn = []
        # Use custom generator to give us row/column positions
        for r, c, label in enumerate_row_column(btn_list, 3):
            # partial takes care of function and argument
            cmd = lambda x=label: self.click(x)
            # create the button
            cur = Button(self.top, text=label, width=10, height=5, command=cmd)
            # position the button
            cur.grid(row=r, column=c)
            btn.append(cur)

    def click(self, label):
        print(label)
        if label == 'Del':
            currentText = self.master.get()
            self.master.delete(0, END)
            self.master.insert(0, currentText[:-1])
        elif label == 'Close':
            self.ok()
        else:
            currentText = self.master.get()
            self.master.delete(0, END)
            self.master.insert(0, currentText + label)

    def ok(self):
        self.top.destroy()
        self.top.master.focus()
"""
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


class Calculator(tk.Tk):

    def __init__(self):
        super().__init__()

        btn_list = ['7', '8', '9', '4', '5', '6', '1', '2', '3', '0', '.', 'Del']
        # create and position all buttons with a for-loop
        btn = []
        # Use custom generator to give us row/column positions
        for r, c, label in enumerate_row_column(btn_list, 3):
            # partial takes care of function and argument
            cmd = lambda x=label: self.click(x)
            # create the button
            cur = Button(numpad, text=label, width=10, height=5, command=cmd)
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

class Calculator2(tk.Tk):

    def __init__(self):
        super().__init__()

        btn_list = ['7', '8', '9', '4', '5', '6', '1', '2', '3', '0', '.', 'Del']
        # create and position all buttons with a for-loop
        btn = []
        # Use custom generator to give us row/column positions
        for r, c, label in enumerate_row_column(btn_list, 3):
            # partial takes care of function and argument
            cmd = lambda x=label: self.click(x)
            # create the button
            cur = Button(numpad2, text=label, width=10, height=5, command=cmd)
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



class YScrolledFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = canvas = tk.Canvas(self, bg='white', relief='raised')
        canvas.grid(row=0, column=0, sticky='nsew')

        scroll = tk.Scrollbar(self, command=canvas.yview, orient=tk.VERTICAL)
        canvas.config(yscrollcommand=scroll.set, width=1024)
        scroll.grid(row=0, column=1, sticky='nsew')

        self.content = tk.Frame(canvas)
        self.canvas.create_window(0, 0, window=self.content, anchor="nw")

        self.bind('<Configure>', self.on_configure)

    def on_configure(self, event):
        bbox = self.content.bbox('ALL')
        self.canvas.config(scrollregion=bbox)

class Notebook(ttk.Notebook):
    def __init__(self, parent, tab_labels):
        super().__init__(parent)

        self._tab = {}
        for text in tab_labels:
            self._tab[text] = YScrolledFrame(self)
            # layout by .add defaults to fill=tk.BOTH, expand=True
            self.add(self._tab[text], text=text, compound=tk.TOP)

    def tab(self, key):
        return self._tab[key].content

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
    mystring = msg.decode('ascii')  # decode n return
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

def saveSettings():
    res = c.execute("SELECT id,name FROM profili WHERE name LIKE ?", (str(monthchoosen.get()),)).fetchone()
    idProfil = int(res[0])
    if not idProfil:
        idProfil = 1

    for key in settingsList:
        c.execute("UPDATE vars SET value = ? WHERE name LIKE '"+key+"' AND idProfil = "+str(idProfil)+"", (float(settingsList[key].get()),))
        conn.commit()

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
        "IDS": int(stepperchoosen.get()),
        "T": 1,
    }

    print(json.dumps(data).encode())
    usb.write(json.dumps(data).encode())
    hearv = hear()
    label.config(text=str(hearv))


def Simpletoggle2():
    data = {
        "A": "spindle",
        "IDS": int(stepperchoosen.get()),
        "T": 0,
    }

    print(json.dumps(data).encode())
    usb.write(json.dumps(data).encode())
    hearv = hear()
    label.config(text=str(hearv))

def initEmptyCombo():
    res = c.execute("SELECT name,value FROM vars WHERE idProfil LIKE ?", (str(1),)).fetchall()
    dbvars = dict(res)

    i = 3
    for var in dbvars:
        tk.Label(canvas_tab2, text=var, font=text_font,anchor='w', width=25).grid(row=i, column=0)
        e1 = Entry(canvas_tab2, font=text_font, width=10)
        e1.grid(row=i, column=1)
        settingsList[var] = e1
        i += 1

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


def moveStepper():

    data = {
        "A": "moveS",
        "IDS": int(stepperchoosen.get()),
        "MS": int(moveStepperInput.get()) * 160,
    }
    print(json.dumps(data).encode())
    usb.write(json.dumps(data).encode())
    hearv = hear()
    label.config(text=str(hearv))

main = tk.Tk()
main.geometry("1024x600")
app=FullScreenApp(main)

"""
notebook = Notebook(main, ['Vrtalka', 'Nastavitve', 'Page 3'])
notebook.grid(row=0, column=0, sticky='nsew')
tab1 = notebook.tab('Vrtalka')
tab2 = notebook.tab('Nastavitve')
tab3 = notebook.tab('Page 3')
"""


notebook = ttk.Notebook(main, width=1000, height=600)

# create frames
tab1 = ttk.Frame(notebook, width=1000, height=550)
tab2 = ttk.Frame(notebook, width=1000, height=550)
tab3 = ttk.Frame(notebook, width=1000, height=550)

# add frames to notebook

notebook.add(tab1, text='Vrtalka')
notebook.add(tab2, text='Nastavitve')
notebook.add(tab3, text='Profile')
notebook.pack(side=TOP)


canvas_tab2 = ScrollableFrame(tab2, height=500, width=590, hscroll=False, vscroll=True)
canvas_tab2.pack(side=LEFT, expand=True, anchor='w')

numpad = ttk.Frame(tab2, width=310, height=500)
numpad.pack(expand=True, anchor='e')


canvas_tab3 = ScrollableFrame(tab3, height=500, width=690, hscroll=False, vscroll=True)
canvas_tab3.pack(side=LEFT, expand=True, anchor='w')

numpad2 = ttk.Frame(tab3, width=310, height=500)
numpad2.pack(expand=True, anchor='e')

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
text_font = ('Courier New', '18')

monthchoosen = ttk.Combobox(canvas_tab2, width=27,textvariable=n,font=text_font)
# Adding combobox drop down list
monthchoosen['values'] = list(profilList.values())
monthchoosen.grid(column=0, row=0)
main.option_add('*TCombobox*Listbox.font', text_font)
initEmptyCombo()

stepperchoosen = ttk.Combobox(canvas_tab3, width=27,textvariable=n,font=text_font)
# Adding combobox drop down list
stepperchoosen['values'] = [1,2,3,4,5,6,7]
stepperchoosen.grid(column=0, row=0)
main.option_add('*TCombobox*Listbox.font', text_font)

tk.Label(canvas_tab3, text="Premakni za: ", font=text_font,anchor='w', width=25).grid(row=1, column=0)
moveStepperInput = Entry(canvas_tab3, font=text_font)
moveStepperInput.grid(row=1, column=1)

stepperButton = Button(canvas_tab3, text='Premakni stepper', command=moveStepper, width=20,bg='brown',fg='white').grid(column=1, row=2)
saveSett = Button(canvas_tab2, text='Submit', command=saveSettings, width=20,bg='brown',fg='white').grid(column=1, row=0)
toggle_button = Button(canvas_tab3,text="OFF", width=10, command=Simpletoggle).grid(column=1, row=6)
toggle_button2 = Button(canvas_tab3,text="ON", width=10, command=Simpletoggle2).grid(column=1, row=7)

Calculator()
Calculator2()
main.bind("<FocusIn>", handle_focus)
main.bind("<FocusOut>", handle_focus_lost)

main.mainloop()
