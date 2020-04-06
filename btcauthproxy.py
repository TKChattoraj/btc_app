from python_bitcoinrpc_master.bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

rpc_user = "satoshi"
rpc_password = "1350Redbud"

rpc_connection = AuthServiceProxy("http://%s:%s@192.168.1.15:8332"%(rpc_user, rpc_password))

# best_block_hash = rpc_connection.getbestblockhash()
# print(rpc_connection.getblock(best_block_hash))

print(rpc_connection.getdifficulty())

