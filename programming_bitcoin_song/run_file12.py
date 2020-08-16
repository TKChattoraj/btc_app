import math
from io import BytesIO
from importlib import reload
from helper import run, hash256, little_endian_to_int, decode_base58, int_to_little_endian, hash160
import ecc
from ecc import PrivateKey
import helper
from helper import TWO_WEEKS, calculate_new_bits, murmur3, bit_field_to_bytes, decode_base58
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
from network import SimpleNode, GetHeadersMessage, HeadersMessage, GetDataMessage, FILTERED_BLOCK_DATA_TYPE, TX_DATA_TYPE, BLOCK_DATA_TYPE
import merkleblock
from merkleblock import MerkleBlock
from bloomfilter import BloomFilter, BIP37_CONSTANT, BloomFilterTest

#
# Exercise 1
#
# print("Exercise 2")
# bit_field_size = 10
# bit_field = [0] * bit_field_size
# items = (b'hello world', b'goodbye')
# for item in items:
#     hash = hash160(item)
#     i = int.from_bytes(hash, "big")
#     bit_field[i % bit_field_size] = 1
# print(bit_field)

#
# Exercise 2
#
# filter = BloomFilter(size=10, function_count=5, tweak=99)

# items = (b'Hello World', b'Goodbye!')
# for item in items:
#     for i in range(filter.function_count):
#         seed = i * BIP37_CONSTANT + filter.tweak
#         hash = murmur3(item, seed=seed)
#         bit = hash % len(filter.bit_field)
#         filter.bit_field[bit] = 1
# print(bit_field_to_bytes(filter.bit_field).hex())

        
#
# Exercise 3
#
# print("Exercise 3")
# run(BloomFilterTest("test_add"))

# bit_field = [0,1,0,1,0,1,1,0,1,0,0,0,0,0,0,1]
# r = helper.bit_field_to_bytes(bit_field)

#
# Exercise 4
#
# print("Exercise 4")
# run(BloomFilterTest('test_filterload'))

#
# Exercise 5
#
# print("Exercise 5")
# run(network.GetDataMessageTest('test_serialize'))

# 
# Exercise 6
#
print("Exercise 6")

block_hash_hex = "00000000000001c56dc26dd2ad91860a7fe3fe23bbf00f09ff378f1f69bea512"

# utxo_address = "mqJ8CrnEEUbeMFQ628e99P3RAATbarrQwK"
# utxo_address_h160 = decode_base58(utxo_address)

# bf = BloomFilter(size=30, function_count=5, tweak=45324)
# bf.add(utxo_address_h160)


node = SimpleNode('testnet.programmingbitcoin.com', testnet=True, logging=False)
# node.handshake()
# node.send(bf.filterload())

# getdata = GetDataMessage()
# getdata.add_data(FILTERED_BLOCK_DATA_TYPE, bytes.fromhex(block_hash_hex))

# node.send(getdata)

# found = False
# while not found:
#     message = node.wait_for(MerkleBlock, Tx)
#     if message.command == b'merkleblock':
#         if not message.is_valid():
#             raise RuntimeError('invalid merkle proof')
#     else:
#         for i, tx_out in enumerate(message.tx_outs):
#             if tx_out.script_pubkey.address(testnet=True) == utxo_address:
#                 print('found: {}:{}'.format(message.id(), i))
#                 found = True
#                 break

node.handshake()
getdata = GetDataMessage()
t= '1ca6b09df876b19f37548986f331a5360a472fc8a3604b19877dda83a6bfe326'
t_bytes = bytes.fromhex(t)
#getdata.add_data(BLOCK_DATA_TYPE, bytes.fromhex(block_hash_hex))
getdata.add_data(TX_DATA_TYPE, t_bytes)
node.send(getdata)



received_tx = node.wait_for(Tx)
print(received_tx.id() == t_bytes.hex())

# print("Given:  ", block_hash_hex)
# while not found:
#     message = node.wait_for(Block)
#     if message.command == b'block':
#        received_block_hash = message.hash().hex()
       
#        print("Received:  ", received_block_hash)
#        print(received_block_hash == block_hash_hex)
#        print(message.tx_hashes)
#        found = True
#        break   
