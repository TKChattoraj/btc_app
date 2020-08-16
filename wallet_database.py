from Crypto.Random import random
import sqlite3
import math

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
        print("in retrieve keys")
        retrieve_payee_keys_querry = """ SELECT id, private_key, public_key FROM keys where status= ?"""
        status = "available"
        try:
            retrieved_keys = self.cursor.execute(retrieve_payee_keys_querry, (status,)).fetchall()
            self.connection.commit()
            self.cursor.close()
            print(retrieved_keys)
            return retrieved_keys
        except sqlite3.Error as error:
            print("Error while retrieving possible payees", error)
    
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

    def update_utxo(self, utxo_id, utxo_index, utxo_amount, id):
        update_utxo_querry = """ UPDATE keys SET utxo_id = ?, out_index = ?, amount = ? WHERE id = ? """
        try:
            self.cursor.execute(update_utxo_querry, (utxo_id, utxo_index, utxo_amount, id))
            
        except sqlite3.Error as error:
            print("Error updating the utxos ", error)
        self.connection.commit()
        self.cursor.close()

    def update_wallet_status_ready(self, array):
        # array is tuple of items
        # item[0] is the db_id
        # item[1] is the address
        # item[2] is the IntVar so item[2].get() is the amount value
        update_status_ready_querry = """ UPDATE keys SET status = ? WHERE id =? """
        status = "ready"
        querry_data_list = [(status, item[0]) for item in array]
        print("querry data list: {}".format(querry_data_list))
        try:
            self.cursor.executemany(update_status_ready_querry, querry_data_list)
        except sqlite3.Error as error:
            print("Error updating the ready status ", error)
        self.connection.commit()
        self.cursor.close()


    def get_utxo(self, id):
        get_utxo_querry ="""SELECT utxo_id, out_index, amount FROM keys where id = ? """
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
        get_utxo_row_querry ="""SELECT * FROM keys where id = ? """
        try:
            utxo_result=self.cursor.execute(get_utxo_row_querry, (id,)).fetchone()
            self.connection.commit()
            self.cursor.close()
            print("printing utxo result")
            print(utxo_result, utxo_result[0])
            return(utxo_result[0], utxo_result[1], utxo_result[2], utxo_result[3], utxo_result[4], utxo_result[5])
        except sqlite3.Error as error:
            print("Error getting the utxo ", error)
            self.connection.commit()
            self.cursor.close()


    # retrieve from the wallet database those rows that are actual utxos, i.e. having tx_ids, but not spent
    def get_utxo_rows(self):
        get_utxo_rows_querry ="""SELECT * FROM keys where status = ? """
        try:
            utxos_result_array=self.cursor.execute(get_utxo_rows_querry, ('utxo',)).fetchall()
            self.connection.commit()
            self.cursor.close()
            print("printing utxo result")
            print(utxos_result_array)
            return(utxos_result_array)
        except sqlite3.Error as error:
            print("Error getting the utxos ", error)
            self.connection.commit()
            self.cursor.close()

