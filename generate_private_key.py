import sys
# sys.path.append('./blocksmith-master/blocksmith/')
sys.path.append('./programming_bitcoin_song/')
# from generator import KeyGenerator

import os
from ecc import PrivateKey

private_key_int = int.from_bytes(os.urandom(32), byteorder='big', signed=False)

private_key_obj = PrivateKey(private_key_int)
print(private_key_int)
print(private_key_obj.secret)
print(private_key_obj.point)


# kg = KeyGenerator()
# kg.seed_input('Who is John Galt?')
# private_key = kg.generate_key()
# print(private_key)
# print(len(private_key))