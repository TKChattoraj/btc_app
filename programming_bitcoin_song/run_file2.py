import math

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



#Second Single Input Tx.


prev_tx = bytes.fromhex('38121b96759e12157f80691ee16be9b9641ee0dd1dcb498205e4859992e12822')
prev_tx_obj = TxFetcher.fetch(tx_id=prev_tx.hex(), testnet=True)
print(prev_tx_obj)
txi = TxIn(prev_tx=prev_tx, prev_index=0)
print ("txi:  ", txi)
input_secret = 'd4cfd9eacdfe09205bacff1db49f0d745910f1dae35eaf0b9d490493649326b5'
input_secret_bytes = bytes.fromhex(input_secret)
input_secret_int = int.from_bytes(input_secret_bytes, byteorder= 'big')
input_private_key = PrivateKey(input_secret_int)


pay_secret = 32657585211482469506233837931381064842718320389980770759866880477495824497516
#pay_secret = random.getrandbits(256)
pay_private_key = PrivateKey(pay_secret)
output_address = pay_private_key.point.address(testnet=True)
# out1_address resulting from the above pay_secret
# out1_address = 'mgbxvp8L3o5zbw8P81VWVv42gUj9eZNjAN'

change_secret = 9883161471906162552674337436001522581212416354973578695250248738884382136882
#secret = random.getrandbits(256)
change_private_key = PrivateKey(change_secret)
change_address = change_private_key.point.address(testnet=True)


paying_amount = prev_tx_obj.tx_outs[0].amount
paid_amount = math.floor(paying_amount * .1)
fee = math.floor(paid_amount * .1)
change_amount = paying_amount - paid_amount - fee

paid_script = p2pkh_script(decode_base58(output_address))
change_script = p2pkh_script(decode_base58(change_address))


tx_out_paid = TxOut(paid_amount, paid_script)


tx_out_change = TxOut(change_amount, change_script)

tx = Tx(1, [txi], [tx_out_paid, tx_out_change], 0, True)

print(tx)


print(tx.sign_input(input_index=0, private_key=input_private_key))
print(tx)
print("tx_in script...")
print(tx.tx_ins[0].script_sig)
print(tx.serialize().hex())
