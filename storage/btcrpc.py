# Connect to a bitcoin node via rpc
#  Based on Sankalp Ghatpande, https://kryptomusing.wordpress.com/2017/06/12/bitcoin-rpc-via-python/
#  
from __future__ import print_function
import time, requests, json
from auth import RPC_USER, RPC_PASSWORD

class RPCHost(object):
    def __init__(self, rpc_user=RPC_USER, rpc_password=RPC_PASSWORD, node_address="192.168.1.15", node_port="8332"):
        self._session = requests.Session()
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password
        self._url = "http://%s:%s@%s:%s"%(rpc_user, rpc_password, node_address, node_port)
        self._headers = {'content-type': 'application/json'}

    def call(self, rpcMethod, *params):
        payload = json.dumps({"method": rpcMethod, "params": list(params), "jsonrpc": "2.0"})
        tries = 5
        hadConnectionFailures = False
        while True:
            try:
                response = self._session.post(self._url, headers=self._headers, data=payload)
                print("Response:  %s"%(response))
            except requests.exceptions.ConnectionError:
                tries -= 1
                if tries == 0:
                    raise Exception('Failed to connect for remote procedure call.')
                hadConnectionFailures = True
                print("Couldn't connect for remote procedure call, will sleep for five seconds and then try again ({} more tries)".format(tries))
                time.sleep(10)
            else:
                if hadConnectionFailures:
                    print('Connected for remote procedure call after retry.')
                break
        if not response.status_code in (200, 500):
            raise Exception('RPC connection failure: ' + str(response.status_code) + ' ' + response.reason)
        responseJSON = response.json()
        print("Response JSON: %s"%(responseJSON))
        if 'error' in responseJSON and responseJSON['error'] != None:
            raise Exception('Error in RPC call: ' + str(responseJSON['error']))
        return responseJSON['result']



# txout = "5b35e60862793746175d4444b35c092d2011615c327b42f1ea66a1b6a251835b"
# txout_range = range(0,23)
# txout_number = 8
# for out in txout_range:
#     host = RPCHost()
#     response = host.call("gettxout", txout, out)

def rpc_gettxout(tx_id, tx_out_num):
    host = RPCHost()
    response = host.call("gettxout", tx_id, tx_out_num)
    return response



from python_bitcoinrpc_master.bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import sys
sys.path.append('./programming_bitcoin_song/')
from io import BytesIO
from programming_bitcoin_song.tx import Tx, TxIn, TxOut

class Connection(object):
    # Connect to your node
    # node is at 192.168.1.15:8332 on the local network
    # use the user and password specified in the node's Bitcoin conf file
    #
    def __init__(self, user=RPC_USER, password=RPC_PASSWORD):
        self.connection = AuthServiceProxy("http://%s:%s@192.168.1.15:8332"%(user, password))

def get_raw_transaction(tx_id):
    # best_block_hash = rpc_connection.getbestblockhash()
    # print(rpc_connection.getblock(best_block_hash))
    # "5b35e60862793746175d4444b35c092d2011615c327b42f1ea66a1b6a251835b"
    # print(rpc_connection.getdifficulty())
    node = Connection()
    raw_tx_hex_string = node.connection.getrawtransaction(tx_id)
    tx_byte = bytearray.fromhex(raw_tx_hex_string)
    tx_stream = BytesIO(tx_byte)
    # return a Tx object
    tx = Tx.parse(tx_stream)
    return tx



