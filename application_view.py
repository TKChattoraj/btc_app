# Application View

#from tkinter import *
import tkinter as tk
from tkinter import ttk

import globals

from wallet_database import MyDatabase

from python_bitcoinrpc_master.bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

import sys
sys.path.append('./programming_bitcoin_song/')
from programming_bitcoin_song.tx import Tx, TxIn, TxOut, Connection, TxFetcher

from io import BytesIO

from python_bitcoinrpc_master.bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from f3_controller import make_keys, show_keys
from f4_controller import create_tx, get_payees, calculate_btc_amount
import f4_view

class ColumnInfo():
    def __init__(self, master):

        self.master = master

        self.column_name = tk.StringVar()
        self.column_type = tk.StringVar()
        self.column_name_entry = ttk.Entry(master, width=25, textvariable=self.column_name)
        self.radio_text=ttk.Radiobutton(master, text="Text", variable=self.column_type, value="TEXT")

        self.radio_int=ttk.Radiobutton(master, text="Integer", variable=self.column_type, value="INTEGER")
        self.radio_blob=ttk.Radiobutton(master, text="Blob", variable=self.column_type, value="BLOB")

        self.radio_numeric=ttk.Radiobutton(master, text="Numeric", variable=self.column_type, value="NUMERIC")
        self.radio_real=ttk.Radiobutton(master, text="Real", variable=self.column_type, value="REAL")
        self.column_name_entry.focus()



class F1Frame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))

        #String Variables
        self.db_name = tk.StringVar()
        self.table_name = tk.StringVar()
        #self.column_name = tk.StringVar()
        self.column_type = tk.StringVar()

        ttk.Label(self, text="Database Name:").grid(column=0, row=0, sticky=tk.W)
        self.db_name_entry = ttk.Entry(self, width =25, textvariable=self.db_name)
        self.db_name_entry.grid(column=0, row=1, sticky=tk.W)

        ttk.Label(self, text="Database Table Name:").grid(column=0, row=2, sticky=tk.W)
        self.table_name_entry = ttk.Entry(self, width=25, textvariable=self.table_name)
        self.table_name_entry.grid(column=0, row=3, sticky=tk.W)

        ttk.Label(self, text="Table Column Name:").grid(column=0, row=4, sticky=tk.W)
        ttk.Label(self, text="Table Column Type:").grid(column=1, columnspan=5, row=4, sticky=tk.W)

        self.add_column_button = ttk.Button(self, text="Add Column", command=self.add_column)
        self.create_table_button = ttk.Button(self, text="Create Table", command=self.create_table)

        self.column_info_list = []

        self.add_column()
        self.widget_order()

    def display_buttons(self, row):
        row=row+1 # row for placement of Add Column button after the column_info_list
        self.add_column_button.grid(column=5, row=row)
        self.create_table_button.grid(column=6, row=row)


    def add_column(self):
        self.column_info_list.append(ColumnInfo(self))
        self.display_columns()


    def display_columns(self):
        row = 5  #This is the row location for the widgets--used for placing the column info widgets
        for index, c_info in enumerate(self.column_info_list):
            row += index
            c_info.column_name_entry.grid(column=0, row=row, sticky=tk.W)
            c_info.radio_text.grid(column=1, row=row, sticky=tk.W)
            c_info.radio_int.grid(column=2, row=row, sticky=tk.W)
            c_info.radio_blob.grid(column=3, row=row, sticky=tk.W)
            c_info.radio_numeric.grid(column=4, row=row, sticky=tk.W)
            c_info.radio_real.grid(column=5, row=row, sticky=tk.W)


        self.display_buttons(row)

    def create_table(self):
        print("Creating table")

        column_info_array = []
        for col in self.column_info_list:
            print("%s, %s"%(col.column_name.get(), col.column_type.get()))
            column_info_array.append((col.column_name.get(), col.column_type.get()))

        db = MyDatabase(self.db_name.get())
        db.create_table(self.table_name.get(), column_info_array)

    def widget_order(self):
        order = [self.db_name_entry, self.table_name_entry]
        for col in self.column_info_list:
            order.extend([col.column_name_entry, col.radio_text, col.radio_int])
        order.extend([self.add_column_button, self.create_table_button])
        for widget in order:
            widget.lift()
        self.db_name_entry.focus()


class F2Frame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tx_info_frame = ttk.Frame(self, padding=(3,3,12,12))
        tx_info_frame['borderwidth'] =2
        tx_info_frame['relief'] = 'sunken'
        #tx_info_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        tx_info_frame.pack(expand=True, fill='both')

        #String Variables
        self.txid = tk.StringVar()


        ttk.Label(tx_info_frame, text="Enter tx id (hex):").grid(column=0, row=0, sticky=tk.W)


        txid_entry = ttk.Entry(tx_info_frame, width = 64, textvariable = self.txid)
        txid_entry.grid(column=0, row=1, sticky=tk.W)


        ttk.Button(tx_info_frame, text="Get tx", command = lambda: self.gettx(tx_info_frame)).grid(column=2, row=1, sticky=tk.W)



        for child in tx_info_frame.winfo_children():
            child.grid_configure(padx=5, pady=5)
        txid_entry.focus() #tells into which widget to initially put the cursor
        master.bind('<Return>', self.gettx)


    def gettx(self, show_master):
        try:
            tx_id = str(self.txid.get())

            #tx = get_raw_transaction(tx_id)
            tx = TxFetcher.fetch(tx_id)
            # as a stub display the amont of the 8th output
            self.show_tx(tx, show_master)
            print(tx)
        except ValueError:
            pass


    def show_tx(self, tx, master):

        show_frame = ttk.Frame(master, padding=(3,3,12,12))
        show_frame.grid(column=0, row=2, sticky=(tk.N, tk.W, tk.E, tk.S))

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



            pr_tx = TxFetcher.fetch(input.prev_tx.hex())
            print("Previous transaction of the input")
            print(pr_tx)
            print("End prevous transaction of the input")

            pr_tx_scriptpubkey=pr_tx.tx_outs[input.prev_index].script_pubkey
            print("input's script pub key: ")
            print(pr_tx_scriptpubkey.cmds[0], pr_tx_scriptpubkey.cmds[1])
            print("end script pub key")

            print("Tx_input witness: ")
            print(input.witness)
            print("End tx input witness:")

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




class F3Frame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        key_frame = ttk.Frame(self, padding=(3,3,12,12))
        key_frame['borderwidth'] =2
        key_frame['relief'] = 'sunken'
        key_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        #key_frame.pack(expand=True, fill='both')

        #String Variables


        ttk.Button(key_frame, text="Create Keys", command = lambda: make_keys(key_frame)).grid(column=0, row=1, sticky=tk.W)

        ttk.Button(key_frame, text="Show Keys", command = lambda: show_keys(key_frame)).grid(column=1, row=1, sticky=tk.W)

        master.bind('<Return>', make_keys)




class F4Frame(ttk.Frame):

    def __init__(self, master):
        # master is a.app.notebook
        # self is a.app.notebook.f4, the F4Frame instance
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=tk.YES)
        print("in F4")

        self.master = master

        # IntVar for the F4 Frame
        self.wallet_amount = tk.IntVar()
        self.wallet_amount.set(self.master.wallet.amount)

        f4_view.initial_view_frame(frame_object=self)



class Notebook(ttk.Notebook):
    def __init__(self, master):
        # master is a.app
        # self is a.app.notebook
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=tk.YES)
        #self.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        #self.db_ops_frame = F1Frame(self)
        self.master = master

        self.wallet=MyDatabase('wallet')
        print("Notebook wallet:  {}".format(self.wallet.amount))

        self.f2 = F2Frame(self) # making the master of a.app.notebook.f2 as a.app.notebook
        self.f3 = F3Frame(self)
        self.f4 = F4Frame(self)


        #self.add(self.db_ops_frame, text ='Database Operations')
        self.add(self.f2, text='Transaction Info')
        self.add(self.f3, text='Generate Keys')
        self.add(self.f4, text='Generate Tx')

class Application(tk.Frame):
    def __init__(self, master=None):
        # self is a.app
        super().__init__(master)
        # master is a.root
        self.master = master
        self.pack(fill=tk.BOTH, expand=tk.YES)
        #self.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))

        self.notebook = Notebook(self)
