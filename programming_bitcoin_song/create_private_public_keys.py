
import math
from helper import run, hash256, little_endian_to_int, decode_base58
from ecc import PrivateKey
import Crypto.Random
from Crypto.Random import random
from utxo import Utxo

def create_keys():
    secret = random.getrandbits(256)    
    private_key = PrivateKey(secret)
    address = private_key.point.address(testnet=True)

    return (private_key.secret, address)

secret, address = create_keys()
print(secret)
print(address)

secret_in_bytes = secret.to_bytes(32, 'big').hex()
print(secret_in_bytes)


u = Utxo(private_key=secret)
u.input_utxo()
