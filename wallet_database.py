from Crypto.Random import random
import sqlite3
import math

import sys
sys.path.append('./programming_bitcoin_song/')
#from programming_bitcoin_song.tx import Tx, TxIn, TxOut, Connection, TxFetcher
from programming_bitcoin_song.ecc import PrivateKey

class MyDatabase:
    """
        create database at 'name'.db file
    """

    def __init__(self, name):
        try:
            self.connection = sqlite3.connect('%s.db'%(name))
            self.cursor = self.connection.cursor()
            self.name = name
            #self.cursor.close()

        except sqlite3.Error as error:
            print("Error while connecitng to sqlite", error)
        # finally:
        #      if (self.connection):
        #          self.connection.close()
        #          print("The SQLite connection is closed")

    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("The SqLite connection is closed")

    def create_table(self, name, column_array):
        qry_str = ""
        for col in column_array:
            qry_str += ", %s %s"%(col[0], col[1])

        sqlite_create_table_querry = """ CREATE TABLE %s (id INTEGER PRIMARY KEY%s ); """%(name, qry_str)
        try:
            self.cursor.execute(sqlite_create_table_querry)
            self.connection.commit()
            print("SQLite table created")
            self.cursor.close()
        except sqlite3.Error as error:
            print("Error whle creating a sqlite table ", error)

    def insert_keys(self, keys_array):
        # key_array needs to be an array of tuples [(private_key, public_key), (), ()....()]
        # private_key is a blob--32 bytes
        # public_key is a blob

        insert_keys_querry = """ INSERT INTO keys (private_key, public_key, status) VALUES(?,?,?)"""
        status = "available"
        insert_keys_data_list = [(item[0], item[1], status) for item in keys_array]
        try:
            self.cursor.executemany(insert_keys_querry, insert_keys_data_list)
            self.connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Error while inserting keys ", error)

    # def update_public_keys(self, key_pairs):
    #     update_public_keys_querry = """ UPDATE keys SET private_key = ?, public_key = ? WHERE private_key = ? """
    #     for pair in key_pairs:
    #         try:
    #             self.cursor.execute(update_public_keys_querry, (pair[0], pair[1], pair[0]))

    #         except sqlite3.Error as error:
    #             print("Error updating the public_keys ", error)
    #     self.connection.commit()
    #     self.cursor.close()

    def retrieve_keys(self):
        retrieve_keys_querry = """ SELECT private_key, public_key FROM keys """
        key_pair_array = []
        try:
            key_pairs = self.cursor.execute(retrieve_keys_querry)
            for pair in key_pairs:
                key_pair_array.append((pair[0], pair[1]))
            self.connection.commit()
            self.cursor.close()
            return key_pair_array
        except sqlite3.Error as error:
            print("Error while retrieving keys ", error)


    def retrieve_keys_for_payee(self):
        #
        # utxo_id being null means the key pair has not been used in a transaction.
        #
        retrieve_payee_keys_querry = """ SELECT id, private_key, public_key FROM keys where utxo_id IS NULL"""

        try:
            retrieved_keys = self.cursor.execute(retrieve_payee_keys_querry).fetchall()

        except sqlite3.Error as error:
            print("Error while retrieving possible payees", error)
        self.connection.commit()
        self.cursor.close()
        return retrieved_keys

    def retrieve_keys_for_utxo_db_id(self, utxo_id):
        print("in retrieve keys for utxo_db_id")
        retrieve_payee_keys_querry = """ SELECT id, private_key, public_key FROM keys where utxo_id = ?"""

        try:
            retrieved_keys = self.cursor.execute(retrieve_payee_keys_querry, (utxo_id,)).fetchall()
        except sqlite3.Error as error:
            print("Error while retrieving possible payees", error)

        self.connection.commit()
        self.cursor.close()
        print(retrieved_keys)
        return retrieved_keys

    def retrieve_change_key(self):
        print("In retrieve change key")
        retrieve_change_key_querry = """ SELECT id, private_key, public_key FROM keys where status = ? """
        status = "available"
        try:
            retrieve_change_key = self.cursor.execute(retrieve_change_key_querry, (status,)).fetchone()
            print("printing retrieved: {}".format(retrieve_change_key))
            print("printing inside tuple:  {}".format(retrieve_change_key[1]))
            self.connection.commit()
            self.cursor.close()
            return retrieve_change_key # returning a tuple:  (id, private_key, public_key)
        except sqlite3.Error as error:
            print("Error while retrieving change key")






    # given the index, keys will return the appropriate private and public keys from the database
    # note:  this procedure is very similar to retriev_keys and so we might need to consolodate
    # maybe not, though as this is a different querry--we'll see.
    #
    def keys(self, index):
        retrieve_keys_querry = """ SELECT private_key, public_key FROM keys where id = ?"""
        try:
            key_pair_result = self.cursor.execute(retrieve_keys_querry, (index,)).fetchall()
            print("result: ")
            print(key_pair_result)
            print("end result")
            self.connection.commit()
            self.cursor.close()
            return (key_pair_result[0][0], key_pair_result[0][1])
        except sqlite3.Error as error:
            print("Error while retrieving keys ", error)

    def update_utxo(self, utxo_list):
        """
            args:  list of tuples (utxo_id, utxo_index, utxo_amount, id)
                    list[0] is utxo_id
                    list[1] is utxo_index
                    list[2] is utxo_amount
                    list[3] is database id

            returns:

        """
        update_utxo_querry = """ UPDATE keys SET utxo_id = ?, out_index = ?, amount = ? WHERE id = ? """

        try:
            self.cursor.executemany(update_utxo_querry, utxo_list)

        except sqlite3.Error as error:
            print("Error updating the utxos ", error)
        self.connection.commit()
        self.cursor.close()


    def get_utxo(self, id):

        get_utxo_querry ="""SELECT utxo_hash, out_index, amount FROM utxo where id = ? """
        try:
            utxo_result=self.cursor.execute(get_utxo_querry, (id,)).fetchall()
            self.connection.commit()
            self.cursor.close()
            return(utxo_result[0][0], utxo_result[0][1], utxo_result[0][2])
        except sqlite3.Error as error:
            print("Error getting the utxo ", error)
            self.connection.commit()
            self.cursor.close()

    def get_utxo_row(self, id):

        get_utxo_row_querry ="""SELECT * FROM utxo where id = ? """
        try:
            # utxos_result will be an array of tuples each
            # (id, utxo_hash, out_index, amount, status)
            utxo_result=self.cursor.execute(get_utxo_row_querry, (id,)).fetchone()
            self.connection.commit()
            self.cursor.close()
            print("printing utxo result")
            print(utxo_result, utxo_result[0])
            return(utxo_result[0], utxo_result[1], utxo_result[2], utxo_result[3], utxo_result[4])
        except sqlite3.Error as error:
            print("Error getting the utxo ", error)
            self.connection.commit()
            self.cursor.close()


    # retrieve from the wallet database those rows that are actual utxos, i.e. having tx_ids, but not spent
    def get_utxo_rows(self):

        get_utxo_rows_querry = """SELECT * FROM utxo where status = ? """
        try:
            # utxos_result_array will be an array of tuples each
            # (id, utxo_hash, out_index, amount, status)
            utxos_result_array=self.cursor.execute(get_utxo_rows_querry, ('utxo',)).fetchall()

        except sqlite3.Error as error:
            print("Error getting the utxos ", error)

        self.connection.commit()
        self.cursor.close()
        return(utxos_result_array)

    @classmethod
    def update_utxo_table_spent(cls, input_update_arg):

        # input_update_arg is a list of tuples: (utxo_hash in bytes, out_index, amount)
        #
        wallet = cls("wallet")
        input_arg = [("spent", arg[0], arg[1], arg[2]) for arg in input_update_arg]

        update_status_querry = """ UPDATE utxo SET status = ? WHERE utxo_hash = ? AND out_index = ? And amount = ? """

        try:
            print("trying to update utxo for spent...")
            wallet.cursor.executemany(update_status_querry, input_arg)
            wallet.connection.commit()
            wallet.cursor.close()
            print("updated utxo for spent")
        except sqlite3.Error as error:
            print("Error updating utxo table status")
            wallet.cursor.close()

    @classmethod
    def insert_new_utxos(cls, new_utxos):
        # new_utxos is a tuple: tx_hash in byets, list of tuples: ([addresses], amount)
        # index of second tuple corresponds to the output index of the pushed tx

        insert_utxos_querry = """ INSERT INTO  utxo (utxo_hash, out_index, amount, status) VALUES (?, ?, ?, ?) """
        tx_hash = new_utxos[0]
        outputs = new_utxos[1]

        status = "utxo"
        insert_data_list = []
        for out_index, out in enumerate(outputs):
            insert_data_list.append((tx_hash, out_index, out[1], status))
        wallet = cls("wallet")
        try:
            wallet.cursor.executemany(insert_utxos_querry, insert_data_list)
            wallet.connection.commit()
            wallet.cursor.close()
        except sqlite3.Error as error:
            print("Error while inserting new utxos ", error)
            wallet.cursor.close()


    def update_just_hash(self):

        update_querry = """ UPDATE utxo SET utxo_hash = ? WHERE id = ? """

        hash_data = [(bytes.fromhex('1379573a272bc1d5b2c6ddf82f0a653d1acb3539f6ee231e2f1c2ed1243812b3'), 1), (bytes.fromhex('0aa127db5e775571f1919bccddc9ef4e52aa3785585a5a26d42fb7282e6ac992'), 2), (bytes.fromhex('0aa127db5e775571f1919bccddc9ef4e52aa3785585a5a26d42fb7282e6ac992'), 3), (bytes.fromhex('0aa127db5e775571f1919bccddc9ef4e52aa3785585a5a26d42fb7282e6ac992'), 4)]

        try:
            self.cursor.executemany(update_querry, hash_data)
            self.connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print("Error while updating just the utxo hash ", error)

    @classmethod
    def update_utxo_for_utxo(cls, t):
        # t is tuple (tx_hash, [([addresses], output amounts)])
        # The index of the address list corresponds to the output index of the tx.
        wallet = cls("wallet")
        tx_hash = t[0]
        addresses_array = t[1] # each item in the addresses_array is an array of addresses
        print("First addresses array: {}".format(addresses_array))
        data = []
        retrieve_data = []
        for i, addresses in enumerate(addresses_array):
            data_tuple = ("utxo", bytes.fromhex(tx_hash), i)
            retrieve_tuple = (bytes.fromhex(tx_hash), i)
            data.append(data_tuple)
            retrieve_data.append(retrieve_tuple)


        update_querry = """ UPDATE utxo SET status = ? WHERE utxo_hash = ? AND out_index = ? """
        retrieve_querry = """ SELECT * FROM utxo where status = ? """
        print(data)
        try:
            wallet.cursor.executemany(update_querry, data)
            wallet.connection.commit()
            wallet.cursor.close()
            print("updated utxo for utxo")
        except sqlite3.Error as error:
            print("Error while updating the utxo for utxo")
            wallet.cursor.close()

        wallet = cls("wallet")

        try:
            utxo_id_array = wallet.cursor.execute(retrieve_querry, ("utxo",)).fetchall()
            wallet.connection.commit()
            print("****************** utxo_id_array********************")
            print(utxo_id_array)
            wallet.cursor.close()
            print("retrieved utxo ids")
        except sqlite3.Error as error:
            print("Error while retrieving the utxo ids")
            wallet.cursor.close()

        update_keys_input = []
        print("second address array: {}".format(addresses_array))

        for i, a in enumerate (addresses_array):
            print(i, a)
            print("Addresses: {}".format(a))
            print("i: {}".format(i))

            out_index = i
            for utxo in utxo_id_array:
                print("utxo[2]")
                if utxo[2] == out_index:
                    input_tuple = (a, utxo[0])
                    update_keys_input.append(input_tuple)
        print(update_keys_input)
        return(update_keys_input)

    @classmethod
    def retrieve_utxo_ids(cls, n):
        # n is a tuple: tx_hash in byets, list of tuples: ([addresses], amount)
        # index of second tuple corresponds to the output index of the pushed tx

        tx_hash = n[0]
        outputs = n[1]

        status = "utxo"
        retrieve_querry = """ SELECT * FROM utxo where utxo_hash = ? """
        querry_data = (tx_hash,)

        wallet = cls("wallet")

        try:
            db_utxo_list = wallet.cursor.execute(retrieve_querry, querry_data).fetchall()
            wallet.connection.commit()
            wallet.cursor.close()
            print("****************** utxo_id_array********************")
            print(db_utxo_list)

            print("retrieved utxo ids")
        except sqlite3.Error as error:
            print("Error while retrieving the utxo ids")
            wallet.cursor.close()

        update_keys_input = []

        for out_index, output in enumerate(outputs):
            for utxo in db_utxo_list:
                print("utxo[2]")
                if utxo[2] == out_index and utxo[3] == output[1]:
                    #input_tuple is (list of addresses, corresponding utxo id)
                    input_tuple = (output[0], utxo[0])
                    update_keys_input.append(input_tuple)
        print(update_keys_input)
        return(update_keys_input)

    @classmethod
    def update_keys_for_utxos(cls, update_keys_input):
        wallet = cls("wallet")
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
        print("********************************")
        print("addresses from db: {}".format(possible_payee_addresses))
        print("********************************")
        print("update_keys_input: {}".format(update_keys_input))
        keys_data = []
        for utxo in update_keys_input:
            # addresses is a list of addresses used for a specific output
            # the list index corresponds to the tx output
            addresses = utxo[0]
            for address in addresses:
                for db_address in possible_payee_addresses:
                    if db_address[1] == address:
                        # this will be the tuple of (utxo_table_id, keys_table_id)
                        # will need to update keys table with the appropriate utxo_id_array
                        tuple=(utxo[1], db_address[0])
                        keys_data.append(tuple)
        print(keys_data)
        print("type: {} {}".format(type(keys_data[0][0]), type(keys_data[0][1])))

        wallet = cls("wallet")
        update_keys_querry = """ UPDATE keys SET utxo_id = ? WHERE id = ? """
        try:
            wallet.cursor.executemany(update_keys_querry, keys_data)
            wallet.connection.commit()
            wallet.cursor.close()
            print("updated keys for utxo_d")
        except sqlite3.Error as error:
            print("Error while updating the keys for utxo_id")
            wallet.cursor.close()

    @classmethod
    def wallet_amount(cls):
        wallet = cls("wallet")
        # utxo_rows is a list of tuples:  (id, utxo_hash, out_index, amount, status)
        utxo_rows=wallet.get_utxo_rows()
        amount = 0
        for utxo in utxo_rows:
            amount += utxo[3]
        return amount
