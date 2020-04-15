from tkinter import *
from tkinter import ttk
from btcrpc import rpc_gettxout

def gettxout(*args):
    try:
        tx_id = str(txid.get())
        tx_out_num = int(tx_output.get())
        # result is the the Json response result dictionary
        result = rpc_gettxout(tx_id, tx_out_num)
        # result["value"] is the utxo value
        if result and result["value"]:
            utxo_value.set(result["value"])
        else: 
            # a response value of None means the utxo is spent already--I think this is true
            utxo_value.set("The utxo is already spent or the response was otherwise null.")

    except ValueError:
        pass


root = Tk()
root.title("Bitcoin Node Interaction")
icon_path = './Cjdowner-Cryptocurrency-Bitcoin.ico'
root.iconbitmap(icon_path)

width = root.winfo_screenwidth()//2
height = root.winfo_screenheight()//2
root.geometry("%sx%s"%(width, height))

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

notebook = ttk.Notebook(root)
notebook.grid(column=0, row=0, sticky=(N,W,E,S))
f1 = ttk.Frame(notebook)
f2 = ttk.Frame(notebook)
f3 = ttk.Frame(notebook)

notebook.add(f1, text ='Transaction Info')
notebook.add(f2, text='Make Transactions')
notebook.add(f3, text='Blockchain Status')

mainframe = ttk.Frame(f1, padding=(3,3,12,12))
mainframe['borderwidth'] =2
mainframe['relief'] = 'sunken'
#mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.pack(expand=True, fill='both')

#String Variables
txid = StringVar()
tx_output = StringVar()
utxo_value = StringVar()

ttk.Label(mainframe, text="txid:").grid(column=0, row=0, sticky=W)
ttk.Label(mainframe, text="tx output:").grid(column=0, row=0, sticky=W)


txid_entry = ttk.Entry(mainframe, width = 64, textvariable = txid)
txid_entry.grid(column=0, row=1, sticky=W)

tx_output_entry = ttk.Entry(mainframe, width = 3, textvariable = tx_output)
tx_output_entry.grid(column=1, row=1, sticky=W)

ttk.Button(mainframe, text="Get utxo", command = gettxout).grid(column=2, row=1, sticky=W)

ttk.Label(mainframe, text="utxo value:").grid(column=0, row=2, sticky=W)
utxo_value.set("utxo value will go here")
utxo_value_label = ttk.Label(mainframe, textvariable=utxo_value)
utxo_value_label.grid(column=0, row=3, sticky=W)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)
txid_entry.focus() #tells into which widget to initially put the cursor
root.bind('<Return>', gettxout)

root.mainloop()