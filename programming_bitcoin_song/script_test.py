from io import BytesIO
from script import Script
from tx import Tx
from helper import encode_varint

# script_sig = '483045022100b660a4532839d67b9a0023fd04fa7a2310794010646b6ef9bab7af636b3bc484022034646d8626e74caefee8df4e54c729c2a207b58b1559e4901ae02e2bfc5d7c7e012103f4a3d0a46dfb7de17d2648de4ea4914b221b496867507e9522182647e8d0badb'

# s = BytesIO(bytes.fromhex(script_sig))
# parsed = Script.parse(s)
# print(parsed)


# tx_hex= '0100000002681fc41cbecc4d8d0b50d59531d7ddb7477d381569bbc671289eb39fbf37753b000000006b483045022100d6a76477022f0a80379fadf0032cf80c70e11e215118524765299f925fe698220220645ec0616950cb233a93d845ef57a8f0f8884a237d8ee2f97cd8ea91099c7578012102370658d5af6a0cbcc3351f831b7159153c674fa0ff736e01509ceba5c5d14b9affffffffc14312c2749052498087e4e38848b9b95b730ca8584f1283dfedaf1a124fdb07000000006a47304402202d460775f9ef47545818fb9fd6e3ccfd96d701fa41ab43f095db854a470d5d270220730094759b54a027a6658dd4d3ebf1a7c7ac8022a0d888d2e84a943c6bf62857012102d36c1120a73be7ab367a9b553db92cc2d66be861da5179b6e7072d8f2e2124c1ffffffff01107a0700000000001976a9146b441f868ae16c367afe74c136fb2da72377992488ac00000000'
# tx_stream = BytesIO(bytes.fromhex(tx_hex))

# tx = Tx.parse(tx_stream, testnet=True)
# print(tx)
# print(tx.tx_ins[0].script_sig)
# print(tx.tx_ins[1].script_sig)


script_pub_key = '76a9146b441f868ae16c367afe74c136fb2da72377992488ac'
script = bytes.fromhex(script_pub_key)
total = len(script_pub_key)
s = encode_varint(total) + script
#script_sig=tx.tx_ins[0].script_sig


stream_spk = BytesIO(s)
parsed_script_pub_key = Script.parse(stream_spk)

print(parsed_script_pub_key)
