from wallet_database import MyDatabase
from programming_bitcoin_song.ecc import PrivateKey


def get_n_public_addresses(wallet,n):
    #key_array = frame_object.master.wallet.retrieve_n_keys(n)
    key_array = wallet.retrieve_n_keys(n)
    n_addresses = []
    for key in key_array:
        private_key = int.from_bytes(key[1], byteorder='big', signed=False)
        #
        # generate the public key from the private key retrieved in the database
        #

        key_object = PrivateKey(private_key)

        # produce the public key address

        ###
        # Update Note:  The public key address will depend on what type of ScriptPubkey
        # will be used.  Assume for now p2pkh--which would require the Base58 of the
        # hash160 of the public key.  p2sh would require the Base58 of the hash160
        # of the Redeem script.
        ###
        # get the compressed sec public key
        compressed = True
        compressed_public_key_address = key_object.point.sec(compressed)

        ##
        # Update Note:  Maybe a verification that the public_key_address just created from the
        # private key is the same address that results from the database public_key.
        # Would need to take that public_key--take it from bytes to dar [?] to base58 [?]
        ##

        # create array of tuples (db_id associated with private_key that make the public_key_address, public_key-address)
        n_addresses.append((key[0], compressed_public_key_address))
    # Return info to the view
    # uncomment when used in the app--comment for temp__run1
    #f4_view.show_possible_payees(frame_object, possible_payee_addresses)
    return n_addresses

wallet = MyDatabase('wallet')
n = 4
addresses = get_n_public_addresses(wallet, n)
print(addresses)
print(len(addresses))
