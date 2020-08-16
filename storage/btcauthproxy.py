from python_bitcoinrpc_master.bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

import sys
sys.path.append('./programming_bitcoin_song/')
from io import BytesIO
from programming_bitcoin_song.tx import Tx, TxIn, TxOut

# rpc_user = "satoshi"
# rpc_password = "1350Redbud"
rpc_user = "Titan"
rpc_password = "MiniTrashMen"

rpc_connection = AuthServiceProxy("http://%s:%s@192.168.1.15:8332"%(rpc_user, rpc_password))

# best_block_hash = rpc_connection.getbestblockhash()
# print(rpc_connection.getblock(best_block_hash))

# print(rpc_connection.getdifficulty())
tx_hex_string = rpc_connection.getrawtransaction("5b35e60862793746175d4444b35c092d2011615c327b42f1ea66a1b6a251835b")
tx_byte = bytearray.fromhex(tx_hex_string)
tx_stream = BytesIO(tx_byte)
tx = Tx.parse(tx_stream)
print(tx)
