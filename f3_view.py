#from tkinter import *

import tkinter as tk
from tkinter import ttk

import f3_controller



def show_keys_view(master, key_pairs):

    ttk.Label(master, text="Private Keys:").grid(column=0, row=3, sticky=tk.W)
    ttk.Label(master, text="Public Keys:").grid(column=1, row=3, sticky=tk.W)
    # show the private key (as hex of bytes making up the private key)
    # show the public key (as hex of the bytes in sec compressed format)
    for i, key in enumerate(key_pairs):
        print(len(key[0]))
        ttk.Label(master, text=key[0].hex()).grid(column=0, row=4+i, sticky=tk.W)
        print(len(key[1]))

        ttk.Label(master, text=key[1].hex()).grid(column=1, row=4+i, sticky=tk.W)