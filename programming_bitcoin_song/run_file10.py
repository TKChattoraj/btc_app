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

from block import Block, BlockTest, GENESIS_BLOCK, LOWEST_BITS

import network
from network import SimpleNode, GetHeadersMessage, HeadersMessage

#
# Exercise 1
#
# print("Exercise 1")
# run(network.NetworkEnvelopeTest("test_parse"))

#
# Exercise 2
#
# print("Exercise 2")
# message_hex = 'f9beb4d976657261636b000000000000000000005df6e0e2'
# message = bytes.fromhex(message_hex)
# message_stream = BytesIO(message)
# envelope = network.NetworkEnvelope.parse(message_stream)
# print(envelope.command)
# print(envelope.payload)

#
# Exercise 3
#
# print("Exercise 3")
# run(network.NetworkEnvelopeTest("test_serialize"))

#
# Exercise 4
#
# print("Exercise 4")
# run(network.VersionMessageTest("test_serialize"))

# 
# Exercise 5
#
# print("Exercise 5")
# run(network.SimpleNodeTest("test_handshake"))

#
# Exercise 6
#
# print("Exercise 6")
# run(network.GetHeadersMessageTest("test_serialize"))

previous = Block.parse(BytesIO(GENESIS_BLOCK))
first_epoch_timestamp = previous.timestamp
expected_bits = LOWEST_BITS
count = 1
node = SimpleNode('mainnet.programmingbitcoin.com', testnet=False)
node.handshake()
for _ in range(19):
    
    getheaders = GetHeadersMessage(start_block=previous.hash())
    node.send(getheaders)
    headers = node.wait_for(HeadersMessage)
    for header in headers.blocks:
        if not header.check_pow():
            raise RuntimeError('bad PoW at block {}'.format(count))
        if header.prev_block != previous.hash():
            raise RuntimeError('discontinuous block at {}'.format(count))
        
        if count % 2016 == 0:
            time_diff = previous.timestamp - first_epoch_timestamp
            expected_bits = calculate_new_bits(previous.bits, time_diff)
            print("Range: {}.  Expected Bits: {}.".format(_, expected_bits.hex()))
            first_epoch_timestamp = header.timestamp
        
        if header.bits != expected_bits:
            raise RuntimeError('bad bits at block {}'.format(count))

        previous = header
        count += 1
