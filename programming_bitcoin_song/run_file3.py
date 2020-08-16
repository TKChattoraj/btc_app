from ecc import PrivateKey
from helper import decode_base58, SIGHASH_ALL
from script import p2pkh_script, Script
from tx import TxIn, TxOut, Tx
from Crypto.Random import random

prev_tx_1 = bytes.fromhex('3b7537bf9fb39e2871c6bb6915387d47b7ddd73195d5500b8d4dccbe1cc41f68')
prev_index_1 = 0
prev_tx_2 = bytes.fromhex('07db4f121aafeddf83124f58a80c735bb9b94888e3e4878049529074c21243c1')
prev_index_2 = 0

# #secret1_hex = '483389c7548e1d393898ed93734263a766899ff53ff730302a75b43b02003b6c'
# #secret1_bytes = bytes.fromhex(secret1_hex)
secret1_int = 67755816702894279448868087164842365456548870436778428099406968593413186895147
# #secret2_hex = '15d9abd132c4a1d77dd0c953b99baa423a3d3f888d7bf7d6e25a7a4333749a32'
# #secret2_bytes = bytes.fromhex(secret2_hex)
secret2_int = 19398006863626223369859239776412679205380440261896921444736015329151679234732


priv1 = PrivateKey(secret=secret1_int)
priv2 = PrivateKey(secret=secret2_int)
priv1_address = priv1.point.address(testnet=True)
priv2_address = priv2.point.address(testnet=True)
# print(priv2_address)

tx_ins = []
tx_ins.append(TxIn(prev_tx_1, prev_index_1))
tx_ins.append(TxIn(prev_tx_2, prev_index_2))

# #out1_secret = random.getrandbits(256)
# #print("output secret:")
# #print(out1_secret)
# #out1_private_key = PrivateKey(out1_secret)
# #out1_address = out1_private_key.point.address(testnet=True) 
# #print("output address:")

target_address = 'mqJ8CrnEEUbeMFQ628e99P3RAATbarrQwK'
target_amount = 499000

h160 = decode_base58(target_address)
script_pubkey = p2pkh_script(h160)
target_satoshis = int(target_amount)


tx_outs = []
tx_outs.append(TxOut(target_satoshis, script_pubkey))
tx_obj = Tx(1, tx_ins, tx_outs, 0, testnet=True)
print(tx_obj.sign_input(0, priv1))

print(tx_obj.sign_input(1, priv2))

print(tx_obj.serialize().hex())

# Two Input Transaction  private keys 6775... and 1939...:
# 0100000002681fc41cbecc4d8d0b50d59531d7ddb7477d381569bbc671289eb39fbf37753b000000006b483045022100a75d4be72872c697fe7ea9154661c256f93329bcb95084746a0117fede161a9e02206a4773d1cc205fa5dda8a22fe43320ec33c3dbe79645379373536df5ee662b57012102370658d5af6a0cbcc3351f831b7159153c674fa0ff736e01509ceba5c5d14b9affffffffc14312c2749052498087e4e38848b9b95b730ca8584f1283dfedaf1a124fdb07000000006b483045022100a87ee9ae8b767ff11efd3abd5c756f1db577b0fb87ac4ba4974f70264bd76df502200a102d6d61cccf8b05348bd92e27931f20480d2559d02fbc635b3664ea311010012102d36c1120a73be7ab367a9b553db92cc2d66be861da5179b6e7072d8f2e2124c1ffffffff01389d0700000000001976a9146b441f868ae16c367afe74c136fb2da72377992488ac00000000

# One Input Transaction private key 6775
# 0100000001681fc41cbecc4d8d0b50d59531d7ddb7477d381569bbc671289eb39fbf37753b000000006b483045022100dd9299f3ea9bee021eaa82c14b8bc76f57135accf4160163eda8636c861d5c67022039cd7bda38d25d9989395ed5f3b36edb8fee9d19e5d3f16551aa7b229776afb8012102370658d5af6a0cbcc3351f831b7159153c674fa0ff736e01509ceba5c5d14b9affffffff01a8cc0300000000001976a9146b441f868ae16c367afe74c136fb2da72377992488ac00000000