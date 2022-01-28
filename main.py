import tkinter as tk
import tkinter.ttk as ttk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.title('Default Demo')
        self.geometry('420x200')

        style = ttk.Style() #If you dont have a class, put your root in the()
        style.configure('TCombobox', arrowsize=100)
        style.configure('Vertical.TScrollbar', arrowsize=100)
        values = []
        for idx in range(1, 50):
            values.append(f'Testing-{idx}')

        cbo = ttk.Combobox(self, values=values)
        cbo.grid(ipady=5)


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()