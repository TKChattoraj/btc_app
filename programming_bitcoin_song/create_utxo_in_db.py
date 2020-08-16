from utxo import Utxo


tx_hash="3b7537bf9fb39e2871c6bb6915387d47b7ddd73195d5500b8d4dccbe1cc41f68"
output_index=0
amount=250000
private_key=67755816702894279448868087164842365456548870436778428099406968593413186895147

key_bytes = private_key.to_bytes(32, 'big').hex()
print(key_bytes)

u = Utxo(prev_tx=tx_hash, output_index=output_index, private_key=private_key, amount=amount)
print(u.prev_tx)
print(u.output_index)
print(u.private_key)
print(u.amount)
u.input_utxo()

tx_hash="07db4f121aafeddf83124f58a80c735bb9b94888e3e4878049529074c21243c1"
output_index=0
amount=250000
private_key=19398006863626223369859239776412679205380440261896921444736015329151679234732

key_bytes = private_key.to_bytes(32, 'big').hex()
print(key_bytes)

u = Utxo(prev_tx=tx_hash, output_index=output_index, private_key=private_key, amount=amount)
print(u.prev_tx)
print(u.output_index)
print(u.private_key)
print(u.amount)
u.input_utxo()
