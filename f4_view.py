#from tkinter import *
import tkinter as tk
from tkinter import ttk

import globals

import threading
import f4_controller

import time

def initial_view_frame(frame_object):
    # frame_object will be the master of the master for the widgets created here
    # frame_object.view will be the frame--the master--for the widgets created here


    initial_view = ttk.Frame(frame_object, padding=(3,3,12,12))
    initial_view['borderwidth'] =2
    initial_view['relief'] = 'sunken'
    initial_view.pack(fill=tk.BOTH, expand=tk.YES)
    #initial_view.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
    frame_object.view = initial_view

    ttk.Label(frame_object.view, text="Wallet Amount: ").grid(column=0, row=0, sticky=tk.W)
    ttk.Label(frame_object.view, text=frame_object.wallet_amount.get()).grid(column=1, row=0, sticky=tk.W)

    ttk.Button(frame_object.view, text="Create Tx", command = lambda: f4_controller.get_payees(frame_object)).grid(column=1, row=2, sticky=tk.W)
    frame_object.master.bind('<Return>', f4_controller.get_payees)


def show_possible_payees(frame_object, possible_payee_addresses):
    #frame_object is the F4Frame instance

    #un-grid the existing view frame in the f4 frame object
    frame_object.view.pack_forget()
    # create the new view frame to be placed in the f4 frame object
    payee_view = ttk.Frame(frame_object, padding=(3,3,12,12))
    payee_view['borderwidth'] =2
    payee_view['relief'] = 'sunken'
    payee_view.pack(fill=tk.BOTH, expand=tk.YES)
    #payee_view.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
    frame_object.view = payee_view

    address_amount_array = []

    ttk.Label(frame_object.view, text="Wallet Amount: ").grid(column=0, row=0, sticky=tk.W)
    ttk.Label(frame_object.view, text= frame_object.wallet_amount.get()).grid(column=1, row=0, sticky=tk.W)

    ttk.Label(frame_object.view, text="Send to the following outputs:").grid(column = 0, row=2, sticky=tk.W)
    ttk.Label(frame_object.view, text="Output Type").grid(column=0, row =3, sticky=tk.W)
    ttk.Label(frame_object.view, text="Address(es)").grid(column =1, row =3, sticky=tk.W)
    ttk.Label(frame_object.view, text= "Amount").grid(column = 2, row=3, sticky=tk.W)

    types = ['p2pkh', 'p2sh']
    type = tk.StringVar()
    #type.set('p2pkh')

    address = tk.StringVar()
    address.set(possible_payee_addresses)
    #typeMenu = ttk.OptionMenu(frame_object.view, type, types[0], *types).grid(column=0, row=4, sticky=tk.W)

    typeMenu = ttk.Combobox(frame_object.view, values=types)
    typeMenu.grid(column=0, row=4, sticky=tk.W)
    typeMenu.bind("<<ComboboxSelected>>", lambda x: getListBox(x, typeMenu, frame_object, possible_payee_addresses))




    # for i, element in enumerate(possible_payee_addresses):
    #
    #     #
    #     #  element is a tuple element (db_id, address)
    #     keys_db_id = element[0]
    #     address = element[1]
    #     amount = tk.IntVar()
    #     amount.set(0)
    #
    #     ttk.Label(frame_object.view, text=address).grid(column =0, row =4+i, sticky=tk.W)
    #     amount_entry = ttk.Entry(frame_object.view, width = 16, textvariable=amount)
    #     amount_entry.grid(column=1, row=4+i, stick=tk.W)
    #
    #     # address_amount_array is an array of tupples (keys_db_id, address, amount)
    #     address_amount_array.append((keys_db_id, address, amount))

    ttk.Button(frame_object.view, text="Proceed", command = lambda: f4_controller.create_tx(frame_object, address_amount_array)).grid(column=3, row=len(address_amount_array)+4)
    frame_object.tx_status.set("Nothing to see here")
    ttk.Label(frame_object.view, textvariable=frame_object.tx_status).grid(column=0, row=6+len(address_amount_array), sticky=tk.W)

############
def getListBox(event, typeMenu, frame_object, addresses):
    print(event)
    print(frame_object, addresses)
    print("Self Value: {}".format(typeMenu.get()))\

    just_addresses = []
    for a in addresses:
        just_addresses.append(a[1])
    if typeMenu.get()=='p2pkh':
        lstaddress = tk.Listbox(frame_object.view, listvariable=just_addresses[0], selectmode=tk.MULTIPLE).grid(column=1, row=4, sticky=tk.W)
    elif typeMenu.get()=='p2sh':
        lstaddress = tk.Listbox(frame_object.view, listvariable=just_addresses, selectmode=tk.MULTIPLE).grid(column=1, row=4, sticky=tk.W)

class UpdateViewThread (threading.Thread):
    def __init__(self, name, parent_frame):
        threading.Thread.__init__(self)
        print("initializing view thread")
        self.name = name
        self.parent_frame = parent_frame
        print("initialing...parent_frame: {}".format(self.parent_frame.tx_status.get()))
        self.running = True
        self.lock = threading.Lock()

    def run(self):
        print("lock: {}".format(self.lock.acquire()))
        while self.running:
          print("in the run")
          print(self.parent_frame.tx_status.get())
          self.update()
        self.parent_frame.tx_status.set("Create Tx Finished!")
        self.parent_frame.view.update()
        self.lock.release()


    def terminate(self):
        self.running = False



    def update(self):

        print("in the update")
        print("before the first parent_frame access")
        print(self.parent_frame.tx_status.get())
        print("after the first parent_frame access")
        self.parent_frame.tx_status.set("Creating the tx")
        print("after the first")
        self.parent_frame.view.update()
        print("Creating the tx")
        time.sleep(1)
        self.parent_frame.tx_status.set("Creating the tx .")
        self.parent_frame.view.update()
        print("Creating the tx .")
        time.sleep(1)
        self.parent_frame.tx_status.set("Creating the tx ..")
        self.parent_frame.view.update()
        print("Creating the tx ..")
        time.sleep(1)
        self.parent_frame.tx_status.set("Creating the tx ...")
        self.parent_frame.view.update()
        print("Creating the tx ...")
        time.sleep(1)
        #parent_frame.after(0, self.update(parent_frame))

############


def show_serialized_tx(master, tx_serialized_hex):
     ttk.Label(master, text= tx_serialized_hex).grid(column =0, row = 20, sticky=tk.W)


def show_tx(frame_object, tx):
    #frame_object is the F4Frame instance

    #un-grid the existing view frame in the f4 frame object
    frame_object.view.pack_forget()


    show_tx_view = ttk.Frame(frame_object, padding=(3,3,12,12))
    show_tx_view['borderwidth'] =2
    show_tx_view['relief'] = 'sunken'
    show_tx_view.pack(fill=tk.BOTH, expand=tk.YES)
    #show_tx_view.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

    frame_object.view = show_tx_view
    #String Variables


    tk.Label(frame_object.view, text="Wallet Amount: ").grid(column=0, row=0, sticky=tk.W)
    ttk.Label(frame_object.view, text= frame_object.wallet_amount.get()).grid(column=1, row=0, sticky=tk.W)

    ttk.Label(show_tx_view, text="tx id: ").grid(column=0, row=2, sticky=tk.W)
    ttk.Label(show_tx_view, text=tx.id()).grid(column=1, columnspan=9, row=2, sticky=tk.W)

    ttk.Label(show_tx_view, text="version: ").grid(column=0, row=3, sticky=tk.W)
    ttk.Label(show_tx_view, text=tx.version).grid(column=1, columnspan=9, row=3, sticky=tk.W)

    ttk.Label(show_tx_view, text="input txs: ").grid(column=0, columnspan=10, row=4, sticky=tk.W)

    for i, input in enumerate(tx.tx_ins):
        ttk.Label(show_tx_view, text="input tx: ").grid(column=1, row=5+i, sticky=tk.W)
        ttk.Label(show_tx_view, text=input.prev_tx.hex()).grid(column=2, columnspan=4, row=5+i, sticky=tk.W)
        ttk.Label(show_tx_view, text="input index: ").grid(column=6, row=5+i, sticky=tk.W)
        ttk.Label(show_tx_view, text=input.prev_index).grid(column=7, row=5+i, sticky=tk.W)
        ttk.Label(show_tx_view, text="input verified: ").grid(column=8, row=5+i, sticky=tk.W)



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

        ttk.Label(show_tx_view, text=verified).grid(column=9, row=5+i, sticky=tk.W)

    ttk.Label(show_tx_view, text="output txs: ").grid(column=0, columnspan=10, row=5+len(tx.tx_ins), sticky=tk.W)

    # define starting row for output
    start = 6 + len(tx.tx_ins)

    for i, output in enumerate(tx.tx_outs):
        ttk.Label(show_tx_view, text="amount: ").grid(column=1, row=start+i, sticky=tk.W)
        ttk.Label(show_tx_view, text=output.amount).grid(column=2, row=start+i, sticky=tk.W)
        ttk.Label(show_tx_view, text="script pub key: ").grid(column=3, row=start+i, sticky=tk.W)
        ttk.Label(show_tx_view, text=output.script_pubkey).grid(column=4, columnspan=6,row=start+i, sticky=tk.W)

    ttk.Label(show_tx_view, text="locktime: ").grid(column=0, row=start+len(tx.tx_outs), sticky=tk.W)
    ttk.Label(show_tx_view, text= tx.locktime).grid(column=1, columnspan=9, row=start+len(tx.tx_outs), sticky=tk.W)


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
