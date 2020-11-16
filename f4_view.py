#from tkinter import *
import tkinter as tk
from tkinter import ttk

import globals

import f4_controller


def show_possible_payees(frame, possible_payee_addresses):

    master = frame.master
    frame.grid_remove()
    payee_frame = ttk.Frame(master, padding=(3,3,12,12))
    payee_frame['borderwidth'] =2
    payee_frame['relief'] = 'sunken'
    payee_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

    address_amount_array = []

    ttk.Label(payee_frame, text="Wallet Amount: ").grid(column=0, row=0, sticky=tk.W)
    ttk.Label(payee_frame, text= globals.btc_amount.get()).grid(column=1, row=0, sticky=tk.W)


    ttk.Label(payee_frame, text="Address").grid(column =0, row =3, sticky=tk.W)
    ttk.Label(payee_frame, text= "Amount").grid(column = 1, row=3, sticky=tk.W)
    for i, element in enumerate(possible_payee_addresses):

        #
        #  element is a tuple element (db_id, address)
        keys_db_id = element[0]
        address = element[1]
        amount = tk.IntVar()
        amount.set(0)

        ttk.Label(payee_frame, text=address).grid(column =0, row =4+i, sticky=tk.W)
        amount_entry = ttk.Entry(payee_frame, width = 16, textvariable=amount)
        amount_entry.grid(column=1, row=4+i, stick=tk.W)

        # address_amount_array is an array of tupples (keys_db_id, address, amount)
        address_amount_array.append((keys_db_id, address, amount))

    ttk.Button(payee_frame, text="Proceed", command = lambda: f4_controller.create_tx(master, address_amount_array)).grid(column=3, row=len(address_amount_array)+4)



def show_serialized_tx(master, tx_serialized_hex):
     ttk.Label(master, text= tx_serialized_hex).grid(column =0, row = 20, sticky=tk.W)


def show_tx(frame, tx):
    master = frame.master
    frame.grid_remove()
    show_frame = ttk.Frame(master, padding=(3,3,12,12))
    show_frame['borderwidth'] =2
    show_frame['relief'] = 'sunken'
    show_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

    #String Variables

    # Integer Variables
    btc_amount = tk.IntVar()

    btc_amount.set(f4_controller.calculate_btc_amount())

    ttk.Label(show_frame, text="Wallet Amount: ").grid(column=0, row=0, sticky=tk.W)
    ttk.Label(show_frame, text= btc_amount.get()).grid(column=1, row=0, sticky=tk.W)

    ttk.Label(show_frame, text="tx id: ").grid(column=0, row=2, sticky=tk.W)
    ttk.Label(show_frame, text=tx.id()).grid(column=1, columnspan=9, row=2, sticky=tk.W)

    ttk.Label(show_frame, text="version: ").grid(column=0, row=3, sticky=tk.W)
    ttk.Label(show_frame, text=tx.version).grid(column=1, columnspan=9, row=3, sticky=tk.W)

    ttk.Label(show_frame, text="input txs: ").grid(column=0, columnspan=10, row=4, sticky=tk.W)

    for i, input in enumerate(tx.tx_ins):
        ttk.Label(show_frame, text="input tx: ").grid(column=1, row=5+i, sticky=tk.W)
        ttk.Label(show_frame, text=input.prev_tx.hex()).grid(column=2, columnspan=4, row=5+i, sticky=tk.W)
        ttk.Label(show_frame, text="input index: ").grid(column=6, row=5+i, sticky=tk.W)
        ttk.Label(show_frame, text=input.prev_index).grid(column=7, row=5+i, sticky=tk.W)
        ttk.Label(show_frame, text="input verified: ").grid(column=8, row=5+i, sticky=tk.W)



        # pr_tx = TxFetcher.fetch(input.prev_tx.hex())
        # print("Previous transaction of the input")
        # print(pr_tx)
        # print("End prevous transaction of the input")
        #
        # pr_tx_scriptpubkey=pr_tx.tx_outs[input.prev_index].script_pubkey
        # print("input's script pub key: ")
        # print(pr_tx_scriptpubkey.cmds[0], pr_tx_scriptpubkey.cmds[1])
        # print("end script pub key")
        #
        # print("Tx_input witness: ")
        # print(input.witness)
        # print("End tx input witness:")

        verified= tx.verify_input(i)
        if verified == 1:
            verified = "Yes"
        else:
            verified = "No"

        ttk.Label(show_frame, text=verified).grid(column=9, row=5+i, sticky=tk.W)

    ttk.Label(show_frame, text="output txs: ").grid(column=0, columnspan=10, row=5+len(tx.tx_ins), sticky=tk.W)

    # define starting row for output
    start = 6 + len(tx.tx_ins)

    for i, output in enumerate(tx.tx_outs):
        ttk.Label(show_frame, text="amount: ").grid(column=1, row=start+i, sticky=tk.W)
        ttk.Label(show_frame, text=output.amount).grid(column=2, row=start+i, sticky=tk.W)
        ttk.Label(show_frame, text="script pub key: ").grid(column=3, row=start+i, sticky=tk.W)
        ttk.Label(show_frame, text=output.script_pubkey).grid(column=4, columnspan=6,row=start+i, sticky=tk.W)

    ttk.Label(show_frame, text="locktime: ").grid(column=0, row=start+len(tx.tx_outs), sticky=tk.W)
    ttk.Label(show_frame, text= tx.locktime).grid(column=1, columnspan=9, row=start+len(tx.tx_outs), sticky=tk.W)


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








#
    #  Following is just display code--don't know if it will remain
    #

            # ttk.Label(master, text="Sending Bitcoins as followings:").grid(column =0, row=8)
            # ttk.Label(master, text="Address").grid(column =0, row =9, sticky=tk.W)
            # ttk.Label(master, text= "Amount").grid(column = 1, row=10, sticky=tk.W)
            # for i, item in enumerate(new_array):

            #     ttk.Label(master, text=item[0]).grid(column =0, row=11+i, sticky=tk.W)
            #     ttk.Label(master, text=item[1].get()).grid(column =1, row=11+i, sticky=tk.W)
