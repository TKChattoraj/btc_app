# Application Controller

#from tkinter import *
import tkinter as tk
from tkinter import ttk

from application_view import ColumnInfo, F1Frame, F2Frame, F3Frame, F4Frame, Notebook, Application

class Application_Controller:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Bitcoin Node Interaction")

        icon_path = './Cjdowner-Cryptocurrency-Bitcoin.ico'
        self.root.iconbitmap(icon_path)

        width = self.root.winfo_screenwidth()//2
        height = self.root.winfo_screenheight()//2
        self.root.geometry("%sx%s"%(width, height))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.app = Application(master = self.root)
        

    def run(self):
        self.app.mainloop()