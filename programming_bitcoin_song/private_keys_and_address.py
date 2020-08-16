import math
from helper import run, hash256, little_endian_to_int, decode_base58
from ecc import PrivateKey
import Crypto.Random
from Crypto.Random import random
from utxo import Utxo

def get_private_key_and_public_address(private_key_hex):
    secret = bytes.fromhex(private_key_hex)
    secret_int = int.from_bytes(secret, byteorder='big')   
    private_key = PrivateKey(secret_int)
    address = private_key.point.address(testnet=True)

    return (private_key.secret, address)


# 111564025536217859302374158907104013725741674789693783505470375588819033115430
secret = 111564025536217859302374158907104013725741674789693783505470375588819033115430
private_key = PrivateKey(secret)
address = private_key.point.address(testnet=True)
secret_bytes = secret.to_bytes(32, 'big')
secret_hex = secret_bytes.hex()
print(secret_hex)
print(address)

# secret, address  = get_private_key_and_public_address('39615436276ea7482438ded7f0a6c5b806e38ebb27fb190b42b84f878a6a84fa')
# print (secret)
# print(address)

# private key/address/txID that can be used to send testnet bitcoin to:


# 67755816702894279448868087164842365456548870436778428099406968593413186895147
# mz3gj4Dm2nT3ZSqDz1hoQL7d149XCuVbbX
# 3b7537bf9fb39e2871c6bb6915387d47b7ddd73195d5500b8d4dccbe1cc41f68
# .0025 BTC Testnet

# 19398006863626223369859239776412679205380440261896921444736015329151679234732
# mtXdymEG4QymhDQ3PeSgKyKPkf4C3U8b4G
# 07db4f121aafeddf83124f58a80c735bb9b94888e3e4878049529074c21243c1
# .0025 BTC Testnet


# 111564025536217859302374158907104013725741674789693783505470375588819033115430
# mqJ8CrnEEUbeMFQ628e99P3RAATbarrQwK
# 1ca6b09df876b19f37548986f331a5360a472fc8a3604b19877dda83a6bfe326
# block hash:  00000000000001d4c3e4c02a71affea52c2473afed674d423b1dc46774fa3985
# .00499 BTC Testnet

# 111564025536217859302374158907104013725741674789693783505470375588819033115430
# mqJ8CrnEEUbeMFQ628e99P3RAATbarrQwK
# 1906b996833e2acb71edc33e3482bd54eedc0c1d77b956758e57688d636f7f6a
# block hash: 00000000000001c56dc26dd2ad91860a7fe3fe23bbf00f09ff378f1f69bea512 
# .00250 BTC Testnet


# 25953797741212637412634694608108635626097262096808737873328470255729285694714
# mw6qP14XyUHQ7YgyUoaaGY21qervCo7nmU
# 9f41ba4dae3b5164a36d81b4c4f8e3777b405a840fe94ab60ee38a742429296e
# .0025 BTC Testnet

