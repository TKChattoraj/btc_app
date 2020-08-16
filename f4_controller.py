# a controller file will house the functions called by the application view frames


# retrieves the utxo from the database wallet given the utxo database id
# # transaction
from wallet_database import MyDatabase


import tkinter as tk
from tkinter import ttk

import sys
sys.path.append('./programming_bitcoin_song/')
from programming_bitcoin_song.tx import Tx, TxIn, TxOut, Connection, TxFetcher
from programming_bitcoin_song.ecc import PrivateKey


from f4_model import TxFactory, Utxo, grab_address

import f4_view

def get_payees(master):
    wallet = MyDatabase("wallet")
    # key_array is array of tuples (db_id, private_key, public_key)
    key_array = wallet.retrieve_keys_for_payee()
    
    
    # make list of possible payee adresses:  
    # 
    possible_payee_addresses = []
    for key in key_array:
        private_key = int.from_bytes(key[1], byteorder='big', signed=False) 
        #
        # generate the public key from the private key retrieved in the database
        # 
    
        key_object = PrivateKey(private_key)
    
        # produce the public key address

        public_key_address = key_object.point.address(testnet=True)

        # create array of tuples (db_id associated with private_key that make the public_key_address, public_key-address)
        possible_payee_addresses.append((key[0], public_key_address))
    
    f4_view.show_possible_payees(master, possible_payee_addresses)



def create_tx(master, array):
    """
        Arguments:
            array:  array of tuples (db_id, address, amount)

        Returns
            tx_serialized.hex():  serialized tx as hex string to be displayed in the f4_view

    """

# Flow will be:

# u=TxFactory.retrieve_utxos() --get from the database the utxos to spend
# tx_ins = u.create_tx_ins_array()
# u.create_output_array()
# tx_outs = u.create_tx_outs_array()
# tx = Tx(1, tx_ins, tx_outs, 0, True) --this will create the tx object--input script_sigs will be '0x00'
# tx.sign_all_inputs(u.utxo_array)

    # create the "material" for a transaction--the "material will be a TxFactory object"

    #
    #  for now we are just going to get the id=1 utxo from the wallet database
    #

    print("Creating the tx...")

    # use list comprehension to remove potential tuples representing utxos (db_id, address, amount) 
    # that aare not to be use, i.e. to which we are not sending Bitcoin

    addresses_to_use = [item for item in array if item[2].get() > 0] # each item will be a tuple (db_id, address, amount)

    # create a TxFactory object--from which the tx will be made

    tx_material = TxFactory()

    # create the TxFactory attribute that holds the utxo factory objects for 
    # the utxos that will be spend, i.e. the inputs
    tx_material.retrieve_utxos()
    # Create the tx_ins objects
    tx_ins = tx_material.create_tx_ins_array()

    tx_material.create_output_array(addresses_to_use)

    # Create the tx_outs object
    tx_outs = tx_material.create_tx_outs_array()
    print(tx_outs)
    
    
    # Create the tx object
    tx = Tx(1,tx_ins, tx_outs, 0, True)
    tx.sign_all_inputs(tx_material.utxo_array)
    print("Tx_ins[0]: {}".format(tx.tx_ins[0]))
    print()
    tx_serialized = tx.serialize()
    print("Tx Serialized: {}".format(tx_serialized.hex()))
    f4_view.show_serialized_tx(master, tx_serialized.hex())
