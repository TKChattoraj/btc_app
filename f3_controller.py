# f3 controller

import tkinter as tk
from tkinter import ttk

from programming_bitcoin_song.ecc import PrivateKey
from programming_bitcoin_song.helper import encode_base58_checksum, hash160

import os
from wallet_database import MyDatabase

import f3_view

def make_keys(master):
    # master will be the master frame for this view, the key_fram from the F3_Frame Clas

    keys_array = []
    
    for i in range(5):
        try:
            # generate the random private key as 32 bytes
            private_key_bytes_generated = os.urandom(32)
            # make the random 32 bytes into an integer
            private_key_int = int.from_bytes(private_key_bytes_generated, byteorder='big', signed=False)
            # create the private/public key object
            key_object = PrivateKey(private_key_int)
            # make the private key into 32 bytes from the key object private key (.secret) as an integer
            private_key_bytes = key_object.secret.to_bytes(32, byteorder='big', signed=False)
            # make the public key in compressed sec format
            public_key_bytes = key_object.point.sec()
            keys_array.append((private_key_bytes, public_key_bytes))
        except ValueError:
            pass
    print(keys_array)
    wallet = MyDatabase("wallet")
    wallet.insert_keys(keys_array)

def show_keys(master):
    # master will be the master frame for this view, the key_frame from the F3_Frame Class
    wallet = MyDatabase("wallet")
    # key_pairs is an array of tuples...(private_key, public_key)
    # private_key is a blob in wif format, public_key is a blob in sec
    
    key_pairs = wallet.retrieve_keys()
    print(key_pairs)
    f3_view.show_keys_view(master, key_pairs)

    # ttk.Label(master, text="Private Keys:").grid(column=0, row=3, sticky=tk.W)
    # ttk.Label(master, text="Public Keys:").grid(column=1, row=3, sticky=tk.W)
    # # show the private key (as hex of bytes making up the private key)
    # # show the public key (as hex of the bytes in sec compressed format)
    # for i, key in enumerate(key_pairs):
    #     print(len(key[0]))
    #     ttk.Label(master, text=key[0].hex()).grid(column=0, row=4+i, sticky=tk.W)
    #     print(len(key[1]))

    #     ttk.Label(master, text=key[1].hex()).grid(column=1, row=4+i, sticky=tk.W)