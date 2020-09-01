#from tkinter import *
import tkinter as tk
from tkinter import ttk



import f4_controller


def show_possible_payees(frame, possible_payee_addresses):
    master = frame
    address_amount_array = []

    ttk.Label(master, text="Address").grid(column =0, row =2, sticky=tk.W)
    ttk.Label(master, text= "Amount").grid(column = 1, row=2, sticky=tk.W)
    for i, element in enumerate(possible_payee_addresses):

        #
        #  element is a tuple element (db_id, address)
        keys_db_id = element[0]
        address = element[1]
        amount = tk.IntVar()
        amount.set(0)

        ttk.Label(master, text=address).grid(column =0, row =3+i, sticky=tk.W)
        amount_entry = ttk.Entry(master, width = 16, textvariable=amount)
        amount_entry.grid(column=1, row=3+i, stick=tk.W)
        address_amount_array.append((keys_db_id, address, amount))

    ttk.Button(master, text="Create Tx", command = lambda: f4_controller.create_tx(master, address_amount_array)).grid(column=3, row=len(address_amount_array)+4)



    #
# Below code is retained for the display of address/amounts
#
# def create_tx_temp(master, array):
#     print("Creating the tx...")
#     # use list comprehension to remove potential utxos that we are not use, i.e. to which we are not sending Bitcoin
#     new_array = [item for item in array if item[1].get() > 0]

#     print(len(new_array))

#     ttk.Label(master, text="Sending Bitcoins as followings:").grid(column =0, row=8)
#     ttk.Label(master, text="Address").grid(column =0, row =9, sticky=tk.W)
#     ttk.Label(master, text= "Amount").grid(column = 1, row=10, sticky=tk.W)
#     for i, item in enumerate(new_array):

#         ttk.Label(master, text=item[0]).grid(column =0, row=11+i, sticky=tk.W)
#         ttk.Label(master, text=item[1].get()).grid(column =1, row=11+i, sticky=tk.W)

def show_serialized_tx(master, tx_serialized_hex):
     ttk.Label(master, text= tx_serialized_hex).grid(column =0, row = 20, sticky=tk.W)


#
    #  Following is just display code--don't know if it will remain
    #

            # ttk.Label(master, text="Sending Bitcoins as followings:").grid(column =0, row=8)
            # ttk.Label(master, text="Address").grid(column =0, row =9, sticky=tk.W)
            # ttk.Label(master, text= "Amount").grid(column = 1, row=10, sticky=tk.W)
            # for i, item in enumerate(new_array):

            #     ttk.Label(master, text=item[0]).grid(column =0, row=11+i, sticky=tk.W)
            #     ttk.Label(master, text=item[1].get()).grid(column =1, row=11+i, sticky=tk.W)
