import math
from io import BytesIO
from importlib import reload
from helper import run, hash256, little_endian_to_int, decode_base58, int_to_little_endian
import ecc
from ecc import PrivateKey
import helper
from helper import TWO_WEEKS, calculate_new_bits
import tx
from tx import TxFetcher, TxTest, TxIn, TxOut, Tx
import script
from script import p2pkh_script
import Crypto.Random
from Crypto.Random import random

from utxo import Utxo, TxFactory
import op
from op import op_checkmultisig

import block
from block import Block, BlockTest, GENESIS_BLOCK, LOWEST_BITS

import network
from network import SimpleNode, GetHeadersMessage, HeadersMessage
import merkelblock


#
# Exercise 1
#
# print("Exercise 1")
# run(helper.HelperTest("test_merkle_parent"))

#
# Exercise 2
#
# print("Exercise 2")
# run(helper.HelperTest("test_merkle_parent_level"))

#
# Exercise 3
#
# print("Exercise 3")
# run(helper.HelperTest("test_merkle_root"))

#
# Exercise 4
#
# print("Exercise 4")
# run(block.BlockTest("test_validate_merkle_root"))

#
# Exercise 5
#
# print("Exercise 5")
# leaves = 27
# if leaves % 2 == 1:
#     leaves += 1
# tree = merkelblock.MerkleTree(leaves)
# print(tree.nodes[0][0])
# print(tree)

#
# Exercise 6
#
# print("Exercise 6")
# run(merkelblock.MerkleBlockTest("test_parse"))

#
# Exercise 7
#
# print("Exercise 7")
# run(merkelblock.MerkleBlockTest("test_is_valid"))
