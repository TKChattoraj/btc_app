import math
from io import BytesIO
from importlib import reload
from helper import run, hash256, little_endian_to_int, decode_base58, int_to_little_endian
import ecc
from ecc import PrivateKey
import helper
from helper import TWO_WEEKS
import tx
from tx import TxFetcher, TxTest, TxIn, TxOut, Tx
import script
from script import p2pkh_script
import Crypto.Random
from Crypto.Random import random

from utxo import Utxo, TxFactory
import op
from op import op_checkmultisig

from block import Block, BlockTest

#
# Exercise 1
#
#run(tx.TxTest("test_is_coinbase"))

#
# Exercise 2
#
#run(tx.TxTest("test_coinbase_height"))

#
# Exercise 3
#
# print("Exercise 3")
# run(BlockTest("test_parse"))

#
# Exercise 4
#
# print("Exercise 4")
# run(BlockTest("test_serialize"))

#
# Exercise 5
#
# print("Exercise 5")
# run(BlockTest("test_hash"))

#
# Exercise 6
# print("Exercise 6")
# run(BlockTest("test_bip9"))

# Exercise 7
#
# print("Exercise 7")
# run(BlockTest("test_bip91"))

# Exercise 8
#
# print("Exercise 8")
# run(BlockTest("test_bip141"))

#
# Exercise 9
#
# print("Exercise 9")
# run(BlockTest("test_target"))

# 
# Exercise 10
#
# print("Exercise 10")
# run(BlockTest("test_difficulty"))

#
# Exercise 11
#
# print("Exercise 11")
# run(BlockTest("test_check_pow"))

#
# Exercise 12
#



block1_hex = '000000203471101bbda3fe307664b3283a9ef0e97d9a38a7eacd8800000000000000000010c8aba8479bbaa5e0848152fd3c2289ca50e1c3e58c9a4faaafbdf5803c5448ddb845597e8b0118e43a81d3'
block2_hex = '02000020f1472d9db4b563c35f97c428ac903f23b7fc055d1cfc26000000000000000000b3f449fcbe1bc4cfbcb8283a0d2c037f961a3fdf2b8bedc144973735eea707e1264258597e8b0118e5f00474'

block1_stream = BytesIO(bytes.fromhex(block1_hex))
block2_stream = BytesIO(bytes.fromhex(block2_hex))
block1 = Block.parse(block1_stream)
block2 = Block.parse(block2_stream)
time_differential = block2.time_differential(block1)
print("time differential:  ", time_differential)
new_target = block1.target() * time_differential//helper.TWO_WEEKS
print("new target: ", new_target)
new_bits = helper.target_to_bits(new_target)
print(new_bits.hex())

print("Doing the other one: *****************")

block1_hex = '000000203471101bbda3fe307664b3283a9ef0e97d9a38a7eacd8800000000000000000010c8aba8479bbaa5e0848152fd3c2289ca50e1c3e58c9a4faaafbdf5803c5448ddb845597e8b0118e43a81d3'
block2_hex = '02000020f1472d9db4b563c35f97c428ac903f23b7fc055d1cfc26000000000000000000b3f449fcbe1bc4cfbcb8283a0d2c037f961a3fdf2b8bedc144973735eea707e1264258597e8b0118e5f00474'
last_block = Block.parse(BytesIO(bytes.fromhex(block2_hex)))
first_block = Block.parse(BytesIO(bytes.fromhex(block1_hex)))
time_differential = last_block.timestamp - first_block.timestamp
print("time differential: ", time_differential)
if time_differential > TWO_WEEKS * 4:
    time_differential = TWO_WEEKS * 4
if time_differential < TWO_WEEKS // 4:
     time_differential = TWO_WEEKS // 4
new_target = last_block.target() * time_differential // TWO_WEEKS
new_bits = helper.target_to_bits(new_target)
print(new_bits.hex())

print("Doing the calculate_new_bits way:  *******************")
block1_hex = '000000203471101bbda3fe307664b3283a9ef0e97d9a38a7eacd8800000000000000000010c8aba8479bbaa5e0848152fd3c2289ca50e1c3e58c9a4faaafbdf5803c5448ddb845597e8b0118e43a81d3'
block2_hex = '02000020f1472d9db4b563c35f97c428ac903f23b7fc055d1cfc26000000000000000000b3f449fcbe1bc4cfbcb8283a0d2c037f961a3fdf2b8bedc144973735eea707e1264258597e8b0118e5f00474'

block1_stream = BytesIO(bytes.fromhex(block1_hex))
block2_stream = BytesIO(bytes.fromhex(block2_hex))
block1 = Block.parse(block1_stream)
block2 = Block.parse(block2_stream)
time_differential = block2.time_differential(block1)
new_bits = helper.calculate_new_bits(block1.bits, time_differential)
print(new_bits.hex())





# parse both blocks
# get the time differential
# if the differential > 8 weeks, set to 8 weeks
# if the differential < 1/2 week, set to 1/2 week
# new target is last target * differential / 2 weeks
# convert new target to bits
# print the new bits hex


# exponent = 4
# coefficient = 1
# target = coefficient * 256**(exponent-3)
# print("target: ", target)
# bits = helper.target_to_bits(target)
# print(bits)


# exponent = 5
# coefficient = 1
# target = coefficient * 256**(exponent-3)
# print("target: ", target)
# bits = helper.target_to_bits(target)
# print(bits)
# target_return = helper.bits_to_target(bits)
# print(target_return)

