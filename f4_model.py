from Crypto.Random import random
import sqlite3
import math

from programming_bitcoin_song.tx import TxFetcher, TxTest, TxIn, TxOut, Tx
from programming_bitcoin_song.script import p2pkh_script
from programming_bitcoin_song.helper import run, hash256, little_endian_to_int, decode_base58
import programming_bitcoin_song.script
from programming_bitcoin_song.ecc import PrivateKey
from wallet_database import MyDatabase

#from tkinter import *
import tkinter as tk
from tkinter import ttk

# Flow will be:
# u=TxFactory.retrieve_utxos() --get from the database the utxos to spend
# tx_ins = u.create_tx_ins_array()
# u.create_output_array()
# tx_outs = u.create_tx_outs_array()
# tx = Tx(1, tx_ins, tx_outs, 0, True) --this will create the tx object--input script_sigs will be '0x00'
# tx.sign_all_inputs(u.utxo_array)


class TxFactory:
    def __init__(self, utxo_array=[], total_input_amount=0, output_array=[], total_paid_amount=0,fee=0, change_amount=0):
        # utxo_array is an array of utxo factory objects--the inputs to making an output_array
        self.utxo_array = utxo_array
        self.total_input_amount = total_input_amount
        self.output_array = output_array
        self.total_paid_amount = total_paid_amount
        self.fee = fee
        self.change_amount = change_amount
        print("TxFactory set up")

    def retrieve_utxos(self):
        """  
            Arguments:
                

            Return:
                :list of utxo factory objects that will be spent
        """
        #
        # Will need to retrive the utxo info from the database and then fetch the transaction
        #
        # Get the utxo info from the database
        #

        wallet = MyDatabase("wallet")
        # get all wallet rows that could be potential utxos to spend, i.e. those with status="utxo"
        # 

        wallet_rows = wallet.get_utxo_rows()
        print("utxos: {}".format(wallet_rows))
        
        pruned_wallet_rows = []  # this is the new list formed with just enough utxos to pay the total_paid_amount

        for utxo in wallet_rows:
            if self.total_input_amount <= self.total_paid_amount:
                pruned_wallet_rows.append(utxo)
                self.total_input_amount += utxo[5]

            # test to see if enough for the fee too
            # assume for now fee < 100000
            if self.total_input_amount > self.total_paid_amount + 100000:  
                break
        if self.total_input_amount < self.total_paid_amount +100000:
            return "Error!  Not enough Bitcoin"
        
        for u in pruned_wallet_rows:

            # u is a tuple housing the row from the database:
            # u[0]:  database id
            # u[1]:  private_key
            # u[2]:  public_key
            # u[3]:  utxo_id
            # u[4]:  out_index
            # u[5]:  amount
            # u[6]:  status

            # get the utxo at database index from the database wallet.db
            db_id, private_key_bytes, public_key_bytes, utxo_id, utxo_index, amount, status = u
            private_key_int = int.from_bytes(private_key_bytes, byteorder='big', signed=False)
            utxo_id_hex = utxo_id.hex()
            print("from database")
            print(private_key_int, public_key_bytes, utxo_id_hex, utxo_index, amount)
            print("******")

            utxo_tx = TxFetcher.fetch(utxo_id_hex, testnet=True, fresh=False)
            print(utxo_tx)

            # get the sript pubkey of the utxo of interest
            utxo_script_pubkey = utxo_tx.tx_outs[utxo_index].script_pubkey
            # determine the script pubkey type
            utxo_script_pubkey_type = utxo_script_pubkey.determine_script_pubkey_type()
            print("utxo script pubkey type:  " + utxo_script_pubkey_type)
            
            #make a utxo factory object from the fetched tx_object
            ut =Utxo(prev_tx=utxo_id, output_index=utxo_index, private_key=private_key_int, amount=amount, id=id)

            # add the utxo factory objec to the factory utxo_array
            self.utxo_array.append(ut)
        return self

    def create_tx_ins_array(self):
        # gather all the input transactions
        
        tx_ins = []
        for u in self.utxo_array:
            prev_tx = u.prev_tx
            txi = TxIn(prev_tx=prev_tx, prev_index=u.output_index)
            tx_ins.append(txi)
        return tx_ins  # returns an array of TxIn objects to become an attribute of a Tx object

    def create_output_array(self, array):
        """
          Arguments:
            array: array of tuples:  (db_id, address, amount)
        
          Returns:
            fills the output_array with utxo factory objects used to create the TxOuts

        """
        ####################################
        # loop to capture an output address/amount pair
        # For each output address/amount pair put into the output_array and add amount to total_paid_amount
        
        # array is an array of (address, amount) tuples
        for item in array:
            # item[0] is the db_id
            # item[1] is the address
            # item[2] is the IntVar so item[2].get() is the amount value
            utxo = Utxo(amount=item[2].get(), address=item[1])  #create a utxo factory object for the output
            self.output_array.append(utxo)
            self.total_paid_amount += item[2].get()
        
        wallet = MyDatabase("wallet")
        wallet.update_wallet_status_ready(array)

        # create change Utxo object
        db_id, change_utxo = self.create_change_element()
        # append the change Utxo to self.output_array
        self.output_array.append(change_utxo)

        wallet.update_wallet_status_ready([(db_id,)])
        #
        #  When the loop is done--will have an array of self.output_array and self.total_paid_amount
        #####################################


    # # Calculate fee

    def calculate_fee(self):
        # for now--just set fee at 50,000 satoshis
        self.fee = 50000


    def create_change_element(self):
        wallet = MyDatabase("wallet")
        self.calculate_fee()
        change_amount = self.total_input_amount - self.total_paid_amount - self.fee

        # get a public_key address to send the change to
        
        change_key = wallet.retrieve_change_key()  # will be a tuple: (db_id, private_key, public_key)
        change_private_key = int.from_bytes(change_key[1], byteorder='big', signed=False)
        change_key_object = PrivateKey(change_private_key)
        change_public_address = change_key_object.point.address(testnet=True)
        change_utxo = Utxo(amount=change_amount, address=change_public_address)
        return (change_key[0],change_utxo)



    def create_tx_outs_array(self):
        print("in create_tx_outs_array")
        tx_outs = []     
        for o in self.output_array:
            #####
            # will need to offer choices as to how the script pubkey for the utxo should be
            #
            # for now create script public key hash
            #####
            paid_script = p2pkh_script(decode_base58(o.address))
            tx_out_paid = TxOut(o.amount, paid_script)
            tx_outs.append(tx_out_paid)
        return tx_outs # returns an array of TxOut objects to become an attribute of a Tx object

    #  retrieve_utxos will get the utxos from the database and return a TxFactory
    #  This will be the start of making a transaction
    
    
                

class Utxo:
    def __init__(self, prev_tx=None, output_index=None, private_key=None, amount=None, id=None, address=None):
        self.id = id
        self.prev_tx = prev_tx
        self.output_index = output_index
        self.private_key = private_key  #private_key is an integer when an attribute of Utxo
        self.amount = amount
        self.address = address
        print("Utxo created: ", self.id, self.prev_tx, self.private_key)
    

def grab_address(id):
    """  Returns the Base58 with checksum address for the public key calculated from the private key stored in the wallet database
        Arguments:
            :id  None right now--but will need to give the database id to tell which private key to retrieve
        Return:
            :str  Base58 address
    """
    #
    # Get the private and public keys from the database given the id
    #

    wallet = MyDatabase("wallet")
    # key_pairs is an array of tuples...(private_key, public_key)
    # private_key is a blob in wif format, public_key is a blob in sec

    #### !
    #### !  right now hardwiring in the id=1, but will need to make that user specifiable
    #### !
    id=id
    # key_pairs is a private, public key tuple
    key_pairs = wallet.keys(id)

    # private_key is a bytes object that should be interpreted as an big endian integer
    # public_key is a bytes object that of the compressed sec public point.
    private_key_bytes, public_key_bytes = key_pairs
    private_key_int = int.from_bytes(private_key_bytes, byteorder='big', signed=False)

    #
    # generate the public key from the private key retrieved in the database
    # 
    
    key_object = PrivateKey(private_key_int)
    
    # produce the public key address

    public_key_address = key_object.point.address(testnet=True)

    print("address: {}".format(public_key_address))
    return public_key_address