
import math
from io import BytesIO
from importlib import reload
from helper import run, hash256, little_endian_to_int, decode_base58
import ecc
from ecc import PrivateKey
import helper
from tx import TxFetcher, TxTest, TxIn, TxOut, Tx
from script import p2pkh_script
import Crypto.Random
from Crypto.Random import random
import script
from utxo import Utxo, TxFactory

# #tx = tx.TxFetcher.fetch('fa1b4db871849a681f5c2f65db4689b126242d8d72e24a9b2fdea2a0318ea974', testnet=True)
# #tx = tx.TxFetcher.fetch('07740fe2068c5582919c9dbbce042b73aeb9cbe7667d4805c40619bb6659b5d0', testnet=False)
# tx = TxFetcher.fetch('452c629d67e41baec3ac6f04fe744b4b9617f8f859c63b3002f8684e7a4fee03', testnet=False)
# print(tx)

# z = tx.sig_hash(0)

# print(z)
# print(type(z))
# run(TxTest("test_sig_hash"))


# Ultimealy the secret is a 256 bit cryptographically random number
# Using hash256 below is just getting a 256 bit number to replicate a secret
#  

# secret = random.getrandbits(256)
# print(type(secret))
# print(secret.to_bytes(32, 'big').hex())
# private_key = PrivateKey(secret)


# secret = little_endian_to_int(hash256(b'And this one belongs to the Reds...tarun@chattoraj.io'))
# print(secret.to_bytes(32, 'big').hex())
# print(type(secret))


# private_key = PrivateKey(secret)
# address = private_key.point.address(testnet=True)
# print(address)
# address_hash = decode_base58(address)
# print("address:  ", address)
# print("address type: ", type(address))
# print("address_hash",  address_hash.hex())





# utxo_array = retrieve_utxos()
# tx_ins = create_tx_ins_array(utxo_array)
# output_array = create_output_array()
# tx_outs, total_paid_amount = create_tx_outs_array(utxo_array, output_array)
# fee = calculate_fee(total_paid_amount)
# change_address = 'change address' #change_address in Base58
# tx_outs = include_change_output(fee, total_paid_amount, change_address, tx_outs)

# Create the tx with x00 script sigs at the inputs
#tx = Tx(1, tx_ins, tx_outs, 0, True)  

# prev_tx = bytes.fromhex('f1fdc3efec3e2617efae4cf7c099ad4a4cf603cc7a2136840afea60dd3081ce6')
# prev_tx_obj = TxFetcher.fetch(tx_id=prev_tx.hex(), testnet=True)
# print(prev_tx_obj)
# txi = TxIn(prev_tx=prev_tx, prev_index=0)
# print ("txi:  ", txi)

# output_address = 'mwJn1YPMq7y5F8J3LkC5Hxg9PHyZ5K4cFv'
# paying_amount = prev_tx_obj.tx_outs[0].amount
# paid_amount = math.floor(paying_amount * .6)
# fee = math.floor(paid_amount * .1)
# change_amount = paying_amount - paid_amount - fee
# paid_script = p2pkh_script(decode_base58(output_address))
# change_script = p2pkh_script(address_hash)

# tx_out_paid = TxOut(paid_amount, paid_script)


# tx_out_change = TxOut(change_amount, change_script)

# tx = Tx(1, [txi], [tx_out_paid, tx_out_change], 0, True)

# print(tx)


# print(tx.sign_input(input_index=0, private_key=private_key))
# print(tx)
# print("tx_in script...")
# print(tx.tx_ins[0].script_sig)
# print(tx.serialize().hex())


#
#create a Utxo object and then input its data into the database
#
# prev_tx = '438c4d42ff4ecd5ae268607bcfcf8bfa7227ae2b5f7256de88488ab3c53df7c8'
# output_index = 1
# prev_tx_fetched = TxFetcher.fetch(tx_id=prev_tx, testnet=True)
# amount = prev_tx_fetched.tx_outs[output_index].amount

# Utxo(prev_tx=prev_tx, output_index=output_index, private_key = secret.to_bytes(32, 'big').hex(), amount=amount).input_utxo()
#
#
# 
utxo_list =[7,8]  #retrieve utxos with ids listed in the given list
f=TxFactory.retrieve_utxos(utxo_list) #get the utxos from the database
tx_ins = f.create_tx_ins_array()
#print(tx_ins)
f.create_output_array()
# print(f.output_array[0])
# print(f.output_array[1])

tx_outs = f.create_tx_outs_array()
tx = Tx(1, tx_ins, tx_outs, 0, testnet=True) #this will create the tx object--input script_sigs will be '0x00'
tx.sign_all_inputs(f.utxo_array)

print("Transaction:")
print(tx.version)
print(tx.tx_ins)
print(tx_outs)
print(tx.locktime)

tx_serialized = tx.serialize()
tx_serialized_hex = tx_serialized.hex()
print(tx_serialized_hex)



