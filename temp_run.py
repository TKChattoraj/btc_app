from wallet_database import MyDatabase





# tx_id = "0aa127db5e775571f1919bccddc9ef4e52aa3785585a5a26d42fb7282e6ac992"
# tx_id_bytes = bytes.fromhex(tx_id)
#
# output = [0, 1, 2]
# amounts = [100000, 200001, 649999]
#
#
# wallet = MyDatabase("wallet")
# wallet.update_utxo(tx_id_bytes, 0, 100000, 2)
# wallet = MyDatabase("wallet")
# wallet.update_utxo(tx_id_bytes, 1, 200001, 3)
# wallet = MyDatabase("wallet")
# wallet.update_utxo(tx_id_bytes, 2, 649999, 4)

#wallet = MyDatabase("wallet")
# key_array is array of tuples (db_id, private_key, public_key)

#key_array = wallet.retrieve_keys_for_payee()
#print(key_array)
#keys = wallet.retrieve_keys_for_utxo_db_id(utxo_id=2)
#print(keys)


# wallet = MyDatabase('wallet')
# wallet.update_just_hash()






pushed_tx = {'tx': {'block_height': -1, 'block_index': -1, 'hash': '0aa127db5e775571f1919bccddc9ef4e52aa3785585a5a26d42fb7282e6ac992', 'addresses': ['mwV7paRv7VdcecM1UPc2jLEWYJb9Uk8pzB', 'muArwFiHwKb682YwStc9VdevUeosghzxTq', 'n1fpHjQXCEumdBVKhhJA77aEmsdjNLErNr', 'mkKJzpQbCQacNtKn6n8MR43nF3CX2v8ttP'], 'total': 950000, 'fees': 50000, 'size': 260, 'preference': 'high', 'relayed_by': '216.18.205.180', 'received': '2020-08-22T17:58:52.741500514Z', 'ver': 1, 'double_spend': False, 'vin_sz': 1, 'vout_sz': 3, 'confirmations': 0, 'inputs': [{'prev_hash': '1379573a272bc1d5b2c6ddf82f0a653d1acb3539f6ee231e2f1c2ed1243812b3', 'output_index': 0, 'script': '483045022100fd66ba3d86cd5283479946b47267c47fb1bf47a2eda6de4fd55e1ee4c00b6b46022017492d5215026337d484d2fa8e9c92112394a48fbef1274da76eb32869fe729c0121035f43cc7aef82e9b603cafdc35b3e0b274138c23323eb05f3b7f7c818534120c4', 'output_value': 1000000, 'sequence': 4294967295, 'addresses': ['mwV7paRv7VdcecM1UPc2jLEWYJb9Uk8pzB'], 'script_type': 'pay-to-pubkey-hash', 'age': 1773191}], 'outputs': [{'value': 100000, 'script': '76a91495c4f7f5aa0390f476865a2a416ac0be1125c8ba88ac', 'addresses': ['muArwFiHwKb682YwStc9VdevUeosghzxTq'], 'script_type': 'pay-to-pubkey-hash'}, {'value': 200001, 'script': '76a914dd0f939e30b2ba468d8ce8fac07c512d3dffe3d788ac', 'addresses': ['n1fpHjQXCEumdBVKhhJA77aEmsdjNLErNr'], 'script_type': 'pay-to-pubkey-hash'}, {'value': 649999, 'script': '76a91434a4eb52a487bc2cdc3839355322b3e7d1c028ab88ac', 'addresses': ['mkKJzpQbCQacNtKn6n8MR43nF3CX2v8ttP'], 'script_type': 'pay-to-pubkey-hash'}]}}



def update_utxo_for_spent(pushed_tx):
    tx_inputs = pushed_tx['tx']['inputs']  # array of JSON for certain input values  see above example
    input_update_arg = []
    for input in tx_inputs:
        input_update_arg = [(bytes.fromhex(input['prev_hash']), input['output_index'])]
    MyDatabase.update_db_utxo_table_spent(input_update_arg)

def sort_pushed_tx_for_utxo_update(pushed_tx):
    tx_hash = pushed_tx['tx']['hash']
    # Create an array of arrays of output addresses.
    # The indices of the main array will corespond to the outpu_index of the tx
    outputs = [ output['addresses'] for output in pushed_tx['tx']['outputs']]
    t = (tx_hash, outputs) # where outputs is an array of address arrays
    print(t)
    return t

def update_db_for_utxo():
    t=sort_pushed_tx_for_utxo_update(pushed_tx)
    update_utxo_for_utxo = MyDatabase.update_utxo_for_utxo(t)
    return update_utxo_for_utxo

def update_db_keys_utxos(keys_update_input):
    MyDatabase.update_keys_for_utxos(keys_update_input)

update_utxo_for_spent(pushed_tx)
keys_update_input=update_db_for_utxo()
update_db_keys_utxos(keys_update_input)




Tx Serialized: 010000000292c96a2e28b72fd4265a5a588537aa524eefc9ddcc9b91f17155775edb27a10a000000006b483045022100dc1c67c5850a2514cb1d0f1dc91d68a3b5bff6f07e9f3a042f2a45c56731958e02202dc093b9a9298ce1c0d232634c60eb76e0adac1cc5412ec86c0a19188933babb012103880464dae26caec050429b006e25bd9c04959d2eebf4f9f62d57de5888e2fad5ffffffff92c96a2e28b72fd4265a5a588537aa524eefc9ddcc9b91f17155775edb27a10a010000006a473044022033c0d498cc8952372e18915a84f07fe17e7ea8e04d2a3e2befc108c59d046b610220443871cfa45721b6383ade40be811db472f9d399f28576af8429eebc44cc67d6012103840eddc8de8c5b7fd50f37d3d52ff50166a909c2ffe16fc6b98da5ff62ec5eb0ffffffff02400d0300000000001976a9141cfbec8e963eef41f349c700a4c4f02ec3653fe788ac51c30000000000001976a914085ba10d4d0940e492c8fa7150db4d313b7179b888ac00000000
