import math
from io import BytesIO
from importlib import reload
from helper import run, hash256, little_endian_to_int, decode_base58, int_to_little_endian
import ecc
from ecc import PrivateKey
import helper
import tx
from tx import TxFetcher, TxTest, TxIn, TxOut, Tx
import script
from script import p2pkh_script
import Crypto.Random
from Crypto.Random import random

from utxo import Utxo, TxFactory
import op
from op import op_checkmultisig


# z = 0xe71bfa115715d6fd33796948126f40a8cdd39f187e4afb03896795189fe1423c
# sig0 = bytes.fromhex('3045022100da92655fe37036f47756db8102e0d7d5e28b3beb83a8fef4f5dc0559bddfb94e02205a36d4e4e6c7fcd16658c50783e00c341609977aed3ad00937bf4ee942a8993701')
# sig1 = bytes.fromhex('3045022100dc92655fe37036f47756db8102e0d7d5e28b3beb83a8fef4f5dc0559bddfb94e02205a36d4e4e6c7fcd16658c50783e00c341609977aed3ad00937bf4ee942a8993701')
# sig2 = bytes.fromhex('3045022100da6bee3c93766232079a01639d07fa869598749729ae323eab8eef53577d611b02207bef15429dcadce2121ea07f233115c6f09034c0be68db99980b9a6c5e75402201')
# sec1 = bytes.fromhex('022626e955ea6ea6d98850c994f9107b036b1334f18ca8830bfff1295d21cfdb70')
# sec2 = bytes.fromhex('03b287eaf122eea69030a0e9feed096bed8045c8b98bec453e1ffac7fbdbd4bb71')
# stack = [b'', sig1, sig2, b'\x02', sec1, sec2, b'\x02']
# print(op_checkmultisig(stack, z))
# print(stack)


#
# Exercise 1
#
# reload(op)
# run(op.OpTest('test_op_checkmultisig'))

#
# Exercise 2
#
# reload(op)
# run(helper.HelperTest('test_p2pkh_address'))

#
# Exercise 3
#
# reload(op)
# run(helper.HelperTest('test_p2sh_address'))


#
# Exercise 4
#
# hex_tx = '0100000001868278ed6ddfb6c1ed3ad5f8181eb0c7a385aa0836f01d5e4789e6bd304d87221a000000db00483045022100dc92655fe37036f47756db8102e0d7d5e28b3beb83a8fef4f5dc0559bddfb94e02205a36d4e4e6c7fcd16658c50783e00c341609977aed3ad00937bf4ee942a8993701483045022100da6bee3c93766232079a01639d07fa869598749729ae323eab8eef53577d611b02207bef15429dcadce2121ea07f233115c6f09034c0be68db99980b9a6c5e75402201475221022626e955ea6ea6d98850c994f9107b036b1334f18ca8830bfff1295d21cfdb702103b287eaf122eea69030a0e9feed096bed8045c8b98bec453e1ffac7fbdbd4bb7152aeffffffff04d3b11400000000001976a914904a49878c0adfc3aa05de7afad2cc15f483a56a88ac7f400900000000001976a914418327e3f3dda4cf5b9089325a4b95abdfa0334088ac722c0c00000000001976a914ba35042cfe9fc66fd35ac2224eebdafd1028ad2788acdc4ace020000000017a91474d691da1574e6b3c192ecfb52cc8984ee7b6c568700000000'
# hex_sec = '03b287eaf122eea69030a0e9feed096bed8045c8b98bec453e1ffac7fbdbd4bb71'
# hex_der = '3045022100da6bee3c93766232079a01639d07fa869598749729ae323eab8eef53577d611b02207bef15429dcadce2121ea07f233115c6f09034c0be68db99980b9a6c5e754022'
# hex_redeem_script = '475221022626e955ea6ea6d98850c994f9107b036b1334f18ca8830bfff1295d21cfdb702103b287eaf122eea69030a0e9feed096bed8045c8b98bec453e1ffac7fbdbd4bb7152ae'
# sec = bytes.fromhex(hex_sec)
# der = bytes.fromhex(hex_der)
# redeem_script = script.Script.parse(BytesIO(bytes.fromhex(hex_redeem_script)))
# stream = BytesIO(bytes.fromhex(hex_tx))



# tx_bytes= bytes.fromhex(hex_tx)
# s = BytesIO(tx_bytes)
# mod_tx = Tx.parse(s, testnet=True)
# mod_tx.tx_ins[0].script_sig = redeem_script

# mod_tx_serialized = mod_tx.serialize()
# #add SIGHASH_ALL:
# mod_tx_serialized += int_to_little_endian(1,4)
# z = hash256(mod_tx_serialized)
# z = int.from_bytes(z,'big')

# This is the thing that will need to be repeated for each signature
# in the multisig
# point = ecc.S256Point.parse(sec)
# sig = ecc.Signature.parse(der)

# print(point.verify(z,sig))


#
# Exercise 5
#
reload(tx)
run(tx.TxTest("test_verify_p2sh"))



