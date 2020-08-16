# retrieves the utxo from the database wallet given the utxo database id
# # transaction
from wallet_database import MyDatabase

from python_bitcoinrpc_master.bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

import sys
sys.path.append('./programming_bitcoin_song/')
from programming_bitcoin_song.tx import Tx, TxIn, TxOut, Connection, TxFetcher
from programming_bitcoin_song.ecc import PrivateKey
from programming_bitcoin_song.helper import encode_base58_checksum, hash160

from io import BytesIO

import os



#
# Get the private and public keys from the database given the id
#

wallet = MyDatabase("wallet")
# key_pairs is an array of tuples...(private_key, public_key)
# private_key is a blob in wif format, public_key is a blob in sec
id=1
# key_pairs is a private, public key tuple
key_pairs = wallet.keys(id)

# private_key is a bytes object that should be interpreted as an big endian integer
# public_key is a bytes object that of the compressed sec public point.
private_key_bytes, public_key_bytes = key_pairs
private_key_int = int.from_bytes(private_key_bytes, byteorder='big', signed=False)

# Generate the address--from the public-key in database and from the private_key
# Check that those two paths result in the same address

#
# generate the address from the public key saved in the database
#

h160 = hash160(public_key_bytes)
# if we are doing testnet, need to add prefix = b'\x6f'
# if we are doing mainnet, need to add prefix = b'\x00'

        # if testnet:
        #     prefix = b'\x6f'
        # else:
        #     prefix = b'\x00'

# assume testnet for now:
prefix = b'\x6f'
public_key_address = encode_base58_checksum(prefix + h160)

#
# generate the public key from the private key retrieved in the database
# 
 
key_object = PrivateKey(private_key_int)
# make the private key into 32 bytes from the key object private key (.secret) as an integer
private_key_bytes = key_object.secret.to_bytes(32, byteorder='big', signed=False)
# make the public key in compressed sec format
public_key_bytes = key_object.point.sec()
privately_generated_public_address = key_object.point.address(testnet=True)

print("public_key_address directly from database: ")
print(public_key_address)
print("********")

print("public_key_address from the private key in database")
print(privately_generated_public_address)
print("**********")

print("Are they equal: ")
print(public_key_address == privately_generated_public_address)
print("******")

# This is the utxo info for the data base id=1 private_key/public_key pair  
# TxID: 1379573a272bc1d5b2c6ddf82f0a653d1acb3539f6ee231e2f1c2ed1243812b3
# Output Index:  0
# Address: mwV7paRv7VdcecM1UPc2jLEWYJb9Uk8pzB
# Amount: 0.01

utxo_id_hex = '1379573a272bc1d5b2c6ddf82f0a653d1acb3539f6ee231e2f1c2ed1243812b3'
utxo_id = bytes.fromhex(utxo_id_hex)
utxo_index = 0
utxo_amount = 0.01 * 100000000

#
# Updating the database "wallet" with the utxo values
# You would need to do this when you create a utxo
#
wallet = MyDatabase("wallet")
id=1
wallet.update_utxo(utxo_id, utxo_index, utxo_amount, id)

#
