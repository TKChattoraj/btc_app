from Crypto.Random import random
import sqlite3
import math

from programming_bitcoin_song.tx import TxFetcher, TxIn, TxOut, Tx
from programming_bitcoin_song.script import p2pkh_script
from programming_bitcoin_song.helper import run, hash256, little_endian_to_int, decode_base58
import programming_bitcoin_song.script
from programming_bitcoin_song.ecc import PrivateKey
from wallet_database import MyDatabase

#from tkinter import *
import tkinter as tk
from tkinter import ttk

from blockcypher import pushtx

# Flow will be:
# u=TxFactory.retrieve_utxos() --get from the database the utxos to spend
# tx_ins = u.create_tx_ins_array()
# u.create_output_array()
# tx_outs = u.create_tx_outs_array()
# tx = Tx(1, tx_ins, tx_outs, 0, True) --this will create the tx object--input script_sigs will be '0x00'
# tx.sign_all_inputs(u.utxo_array)


class TxFactory:
    def __init__(self, utxo_array=[], total_input_amount=0, output_array=[], total_paid_amount=0, fee=0, change_amount=0):
        # utxo_array is an array of utxo factory objects--the inputs to making an output_array
        self.utxo_array = utxo_array
        self.total_input_amount = total_input_amount
        self.output_array = output_array
        self.total_paid_amount = total_paid_amount
        self.fee = fee
        self.change_amount = change_amount
        print("TxFactory set up")

    def calc_paid_amount(self, addresses_to_use):
        self.total_paid_amount = 0
        for address in addresses_to_use:
            self.total_paid_amount += address[2].get()


    def create_factory_input_array(self):
        """
            Arguments:


            Return:
                :list of utxo factory objects that will be used to
                 create the TxIn list.

            Potential Revision Note:
                :Further Revisions:
                    Will need to revise this method to accommodate the witness
                    field if the input is a segwit.  But maybe that won't be
                    required until input is signed.
        """
        #
        # Will need to retrive the utxo info from the database and then fetch the transaction
        #
        # Get the utxo info from the database
        #

        wallet = MyDatabase("wallet")
        #
        # get all wallet rows that could be potential utxos to spend, i.e. those with status="utxo"
        wallet_rows = wallet.get_utxo_rows()  #array of tupples (id, utxo_hash, out_index, amount, status)
        print("utxos: {}".format(wallet_rows))

        pruned_wallet_rows = []  # this is the new list formed with just enough utxos to pay the total_paid_amount and fee

        for utxo in wallet_rows:
            if self.total_input_amount <= self.total_paid_amount + 100000:  #assuming not more than 100000 sats for fee
                pruned_wallet_rows.append(utxo)
                self.total_input_amount += utxo[3]
            else:
                break

        if self.total_input_amount < self.total_paid_amount +100000:
            return "Error!  Not enough Bitcoin"

        for u in pruned_wallet_rows:

            # u is a tuple housing the row from the database:
            # u[0]:  database id
            # u[1]:  utxo_hash
            # u[2]:  out_index
            # u[3]:  amount
            # u[4]:  status

            utxo_db_id, utxo_hash, out_index, amount, status = u

            utxo_hash_hex = utxo_hash.hex()  # tx hash for input in hex

            utxo_tx = TxFetcher.fetch(utxo_hash_hex, testnet=True, fresh=False)
            print(utxo_tx)


            ################################# Moved functionaity to tx.py sign_all_inputs##########
            # # get the private/public keys from the wallet database keys table_name
            # # that point to the utxo database id.
            #
            # wallet = MyDatabase("wallet")
            # # keys_list is a list of tuples: (keys_id, private_key, public_key)
            # keys_list = wallet.retrieve_keys_for_utxo_db_id(utxo_db_id)
            # private_keys = []
            # for pair in keys_list:
            #     private_key_bytes = pair[1]
            #     private_key_int = int.from_bytes(private_key_bytes, byteorder='big', signed=False)
            #     private_keys.append(private_key_int)
            ################################# Moved functionaity to tx.py sign_all_inputs##########


            # get the script pubkey of the utxo of interest
            utxo_script_pubkey = utxo_tx.tx_outs[out_index].script_pubkey
            # determine the script pubkey type
            utxo_script_pubkey_type = utxo_script_pubkey.determine_script_pubkey_type()
            print("utxo script pubkey type:  " + utxo_script_pubkey_type)

            #make a utxo factory object from the fetched tx_object
            ###
            # Assuming for now that only one private key is needed
            # Will need to accommodate mutiple keys to sign a utxo later
            ###
            #ut =Utxo(prev_tx=utxo_hash, output_index=out_index, private_key=private_keys[0], amount=amount, id=utxo_db_id)
            ut =Utxo(prev_tx=utxo_hash, output_index=out_index, amount=amount, id=utxo_db_id)
            # add the utxo factory object to the factory utxo_array

            self.utxo_array.append(ut)
            #
            # Revision for multi-sig:
            # Each index entry in utxo_array is associated with an input transaction.
            # For multisig transactions, we'll need to make an index entry itself an array,
            # holding all the utxos that will make the multisig input.
        return self

    def create_tx_ins_array(self):
        # gather all the input transactions

        tx_ins = []
        for u in self.utxo_array:
            prev_tx = u.prev_tx
            txi = TxIn(prev_tx=prev_tx, prev_index=u.output_index)
            tx_ins.append(txi)
        return tx_ins  # returns an array of TxIn objects to become an attribute of a Tx object

    def create_factory_output_array(self, array):
        """
          Arguments:
            array: array of tuples:  (keys_db_id, address, amount)

          Returns:
            fills the output_array with utxo factory objects used to create the TxOuts

        """
        # pop off the last element, which is the change address: (key_db_id, address, amount)
        change_tuple = array.pop()
        change_list = list(change_tuple)

        ####################################
        # loop to capture an output address/amount pair
        # For each output address/amount pair put into the output_array and add amount to total_paid_amount

        # array is an array of (keys_db_id, address, amount) tuples
        for item in array:
            # item[0] is the keys_db_id
            # item[1] is the address
            # item[2] is the IntVar so item[2].get() is the amount value
            utxo = Utxo(amount=item[2].get(), address=item[1])  #create a utxo factory object for the output
            self.output_array.append(utxo)


        # create change Utxo object

        self.calculate_fee()
        change_amount = self.total_input_amount - self.total_paid_amount - self.fee
        change_list[2] = change_amount
        change_element = tuple(change_list)
        change_utxo = Utxo(amount=change_amount, address=change_element[1])
        # append the change Utxo to self.output_array
        self.output_array.append(change_utxo)
        array.append(change_element)

    # # Calculate fee

    def calculate_fee(self):
        # for now--just set fee at 50,000 satoshis
        self.fee = 50000

    def create_tx_outs_array(self):
        print("in create_tx_outs_array")
        tx_outs = []
        for o in self.output_array:
            #####
            # will need to offer choices as to how the script pubkey for the utxo should be
            #
            # for now create script public key hash
            #####
            script_pubkey = p2pkh_script(decode_base58(o.address))
            tx_out_paid = TxOut(o.amount, script_pubkey)
            tx_outs.append(tx_out_paid)
        return tx_outs # returns an array of TxOut objects to become an attribute of a Tx object

    #  retrieve_utxos will get the utxos from the database and return a TxFactory
    #  This will be the start of making a transaction

    def update_utxos_in_db(self, pushed_tx, addresses_to_use):
        utxo_id = pushed_tx['tx']['hash']
        # addresses_to_use[0]
        # pushed_tx['tx']['outputs'] is an array of JSON:
        #   'value'
        #   'script'
        #   'addresss'  string of addresse paid to
        #   'script_type'
        output_list = pushed_tx['tx']['outputs']

        # want to create a list of tuples.
        # each tuple contains:

#                 list[i][0] is utxo_id
#                 list[i][1] is out_index
#                 list[i][2] is utxo_amount
#                 list[i][3] is database id
        update_arry = []
        for i, output in enumerate(output_list):
            for out_address in output['address']:
                for index, address in enumerate(addresses_to_use):
                    if (address[1] == out_address) and (address[2] == output['value']):
                        adresses_to_use.pop(index)
                        db_id = address[0]
                        utxo_amount = output['value']
                else:
                    print("Error in creating input array to update database utxos")




class Utxo:
    def __init__(self, prev_tx=None, output_index=None, private_key=None, amount=None, id=None, address=None):
        self.id = id
        self.prev_tx = prev_tx
        self.output_index = output_index
        ####
        ##  Will need to revise to accommodate mutliple private keys for one utxo
        ###
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

def push_raw_tx(tx_serialized_hex):
    API_KEY = 'e1d429fefa834a18abb6f16ebd4f557d'
    coin = 'btc-testnet'
    # returns a JSON object:
    """
    Pushed Tx: {'tx': {'block_height': -1, 'block_index': -1, 'hash': '0aa127db5e775571f1919bccddc9ef4e52aa3785585a5a26d42fb7282e6ac992', 'addresses': ['mwV7paRv7VdcecM1UPc2jLEWYJb9Uk8pzB', 'muArwFiHwKb682YwStc9VdevUeosghzxTq', 'n1fpHjQXCEumdBVKhhJA77aEmsdjNLErNr', 'mkKJzpQbCQacNtKn6n8MR43nF3CX2v8ttP'], 'total': 950000, 'fees': 50000, 'size': 260, 'preference': 'high', 'relayed_by': '216.18.205.180', 'received': '2020-08-22T17:58:52.741500514Z', 'ver': 1, 'double_spend': False, 'vin_sz': 1, 'vout_sz': 3, 'confirmations': 0, 'inputs': [{'prev_hash': '1379573a272bc1d5b2c6ddf82f0a653d1acb3539f6ee231e2f1c2ed1243812b3', 'output_index': 0, 'script': '483045022100fd66ba3d86cd5283479946b47267c47fb1bf47a2eda6de4fd55e1ee4c00b6b46022017492d5215026337d484d2fa8e9c92112394a48fbef1274da76eb32869fe729c0121035f43cc7aef82e9b603cafdc35b3e0b274138c23323eb05f3b7f7c818534120c4', 'output_value': 1000000, 'sequence': 4294967295, 'addresses': ['mwV7paRv7VdcecM1UPc2jLEWYJb9Uk8pzB'], 'script_type': 'pay-to-pubkey-hash', 'age': 1773191}], 'outputs': [{'value': 100000, 'script': '76a91495c4f7f5aa0390f476865a2a416ac0be1125c8ba88ac', 'addresses': ['muArwFiHwKb682YwStc9VdevUeosghzxTq'], 'script_type': 'pay-to-pubkey-hash'}, {'value': 200001, 'script': '76a914dd0f939e30b2ba468d8ce8fac07c512d3dffe3d788ac', 'addresses': ['n1fpHjQXCEumdBVKhhJA77aEmsdjNLErNr'], 'script_type': 'pay-to-pubkey-hash'}, {'value': 649999, 'script': '76a91434a4eb52a487bc2cdc3839355322b3e7d1c028ab88ac', 'addresses': ['mkKJzpQbCQacNtKn6n8MR43nF3CX2v8ttP'], 'script_type': 'pay-to-pubkey-hash'}]}}

    """
    return pushtx(tx_hex=tx_serialized_hex, coin_symbol = coin, api_key=API_KEY)


def update_utxo_for_spent(pushed_tx):
    tx_inputs = pushed_tx['tx']['inputs']  # array of JSON for certain input values  see above example
    input_update_arg = []
    for input in tx_inputs:
        input_update_arg.append((bytes.fromhex(input['prev_hash']), input['output_index']))
    MyDatabase.update_db_utxo_table_spent(input_update_arg)

def sort_pushed_tx_for_utxo_update(pushed_tx):
    tx_hash = pushed_tx['tx']['hash']
    # Create an array of arrays of output addresses.
    # The indices of the main array will corespond to the outpu_index of the tx
    outputs = [ output['addresses'] for output in pushed_tx['tx']['outputs']]
    t = (tx_hash, outputs) # where outputs is an array of address arrays
    print(t)
    return t

def update_db_for_utxo(pushed_tx):
    t=sort_pushed_tx_for_utxo_update(pushed_tx)
    update_utxo_for_utxo = MyDatabase.update_utxo_for_utxo(t)
    return update_utxo_for_utxo

def update_db_keys_utxos(keys_update_input):
    MyDatabase.update_keys_for_utxos(keys_update_input)

def inputs_for_new_utxos(pushed_tx):
    tx_hash = bytes.fromhex(pushed_tx['tx']['hash'])
    # Create an array of tuples: ([addresses], amount)
    # The [addresses] are a list of addresses associated with the output,
    # amount is the amount of the outputs
    # The indices of the array of tuples corresponds to the output index of the
    # pushed transaction, i.e. outputs[0] is the 0th output of tx having tx_hash
    #
    outputs = [ (output['addresses'], output['value']) for output in pushed_tx['tx']['outputs']]
    n = (tx_hash, outputs)
    # where outputs is an array of tupls ([addresses], output value)]
    # the index of the outputs array corresponds to the push_tx output index
    return n

def inputs_for_utxo_spents(pushed_tx):
    inputs= pushed_tx['tx']['inputs']
    spents_input = [(bytes.fromhex(input['prev_hash']), input['output_index'], input['output_value']) for input in inputs]

    return(spents_input)

def calculate_wallet_amount():
    wallet_amount = MyDatabase.wallet_amount()
    return(wallet_amount)
