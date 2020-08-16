from io import BytesIO
from unittest import TestCase

import copy
import json
import requests

from ecc import PrivateKey
from helper import (
    encode_varint,
    hash256,
    int_to_little_endian,
    little_endian_to_int,
    read_varint,
    SIGHASH_ALL,
    decode_base58
)


from script import Script, p2pkh_script, p2wsh_script

import sys
sys.path.append('../')

from python_bitcoinrpc_master.bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from auth import RPC_USER, RPC_PASSWORD


class Connection(object):
    # Connect to your node
    # node is at 192.168.1.15:8332 on the local network
    # use the user and password specified in the node's Bitcoin conf file
    #
    def __init__(self, user=RPC_USER, password=RPC_PASSWORD):
        self.connection = AuthServiceProxy("http://%s:%s@192.168.1.15:8332"%(user, password))



class TxFetcher:
    """  Modified TxFetcher 
            For testnet:  go to blockcypher.com
            For mainnet:  go to local node. 
    """
    cache = {}

    @classmethod
    def get_url(cls, testnet=False):
        if testnet:
            #return 'http://testnet.programmingbitcoin.com'
            return 'https://api.blockcypher.com/v1/btc/test3/txs/'
        # else:
        #     #return 'http://mainnet.programmingbitcoin.com'
        #     return 'https://api.blockcypher.com/v1/btc/main/txs/'

    @classmethod
    def fetch(cls, tx_id, testnet=False, fresh=False):
        #if fresh or (tx_id not in cls.cache):
        print("***************in fetch**************")
        if True:                          
            #  Following is the url formating and request for programmingbitcoin.com
            # url = '{}/tx/{}.hex'.format(cls.get_url(testnet), tx_id)    
            # response = requests.get(url)
            
            #  Following is the request for  blockcypher.com
            #  Note:  Need to figure out how to get the raw hex from a mainnet transaction.  Need to look at the blockcypher api as
            #  it doesn't seem as though the option for creating a "hex" json key exists as it does in testnet.
            
            # !
            # will need to re-configure retrieving a testnet tx from the local bitcoin node
            # !

            if testnet:
                url = "{}{}?limit=50&includeHex=true".format(cls.get_url(testnet), tx_id)
                response = requests.get(url)
                get_response = requests.get(url)
                response = get_response.json()
                #  raw tex (in hex) of the retrieved transaction.
                raw_tx = response["hex"]
                print(raw_tx)
                raw = bytes.fromhex(raw_tx)
                tx = Tx.parse(BytesIO(raw), testnet=testnet)

            else:
                node = Connection()
                raw_tx_hex_string = node.connection.getrawtransaction(tx_id)
                print("raw hex of tx:")
                print(raw_tx_hex_string)
                print("end raw hex of tx")

                
                raw = bytes.fromhex(raw_tx_hex_string)
                tx = Tx.parse(BytesIO(raw), testnet=testnet)
                #tx_stream = BytesIO(raw)
                # return a Tx object
                #tx = Tx.parse(tx_stream)
            

                #url = "{}{}?limit=50&includeHex=true".format(cls.get_url(testnet), tx_id)
            
            # get_response = requests.get(url)
            # response = get_response.json()
            # #raw tex (in hex) of the retrieved transaction.
            # raw_tx = response["hex"]
  
            # try:
            #     # Following is converting hex string to bytes as per the programming bitcoin way
            #     #raw = bytes.fromhex(response.text.strip())
                
            #     raw = bytes.fromhex(raw_tx.strip())
                
            # except ValueError:
            #     raise ValueError('unexpected response: {}'.format(response.text))
            # make sure the tx we got matches to the hash we requested

            # ! 
            # The following 'if' seems to remove the segwit marker and segwit flag, but the parse methods now include the possibility of 
            # segwit and so this seems to not be needed or appropriate anymore.
            # !
            # if raw[4] == 0:
            #     print("raw 4")
            #     print(raw[4])
            #     raw = raw[:4] + raw[6:]
            #     tx = Tx.parse(BytesIO(raw), testnet=testnet)
            #     tx.locktime = little_endian_to_int(raw[-4:])
            # else:
            #     tx = Tx.parse(BytesIO(raw), testnet=testnet)
            #!

            
            if tx.id() != tx_id:
                raise ValueError('not the same id: {} vs {}'.format(tx.id(), tx_id))
            cls.cache[tx_id] = tx
        cls.cache[tx_id].testnet = testnet
        print("***************out fetch**************")
        return cls.cache[tx_id]

    @classmethod
    def load_cache(cls, filename):
        disk_cache = json.loads(open(filename, 'r').read())
        for k, raw_hex in disk_cache.items():
            raw = bytes.fromhex(raw_hex)
            if raw[4] == 0:
                raw = raw[:4] + raw[6:]
                tx = Tx.parse(BytesIO(raw))
                tx.locktime = little_endian_to_int(raw[-4:])
            else:
                tx = Tx.parse(BytesIO(raw))
            cls.cache[k] = tx

    @classmethod
    def dump_cache(cls, filename):
        with open(filename, 'w') as f:
            to_dump = {k: tx.serialize().hex() for k, tx in cls.cache.items()}
            s = json.dumps(to_dump, sort_keys=True, indent=4)
            f.write(s)


class Tx:

    command = b'tx'

    def __init__(self, version, tx_ins, tx_outs, locktime, testnet=False, segwit=False):
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime
        self.testnet = testnet
        self.segwit = segwit
        self._hash_prevouts = None
        self._hash_sequence = None
        self._hash_outputs = None
    

    def __repr__(self):
        tx_ins = ''
        for tx_in in self.tx_ins:
            tx_ins += tx_in.__repr__() + '\n'
        tx_outs = ''
        for tx_out in self.tx_outs:
            tx_outs += tx_out.__repr__() + '\n'
        return 'tx: {}\nversion: {}\ntx_ins:\n{}tx_outs:\n{}locktime: {}'.format(
            self.id(),
            self.version,
            tx_ins,
            tx_outs,
            self.locktime
        )

 
    def id(self):
        '''Human-readable hexadecimal of the transaction hash'''
        return self.hash().hex()

    def hash(self):
        '''Binary hash of the legacy serialization'''
        return hash256(self.serialize_legacy())[::-1]
    
    @classmethod
    def parse(cls, s, testnet=False):
        s.read(4)
        marker = s.read(1)
        print("marker: ")
        print(marker)
        if marker == b'\x00':
            parse_method = cls.parse_segwit
        else: 
            parse_method = cls.parse_legacy
        s.seek(-5, 1)
        return parse_method(s, testnet=testnet)


    @classmethod
    def parse_legacy(cls, s, testnet=False):
        print("in parse legacy")
        '''Takes a byte stream and parses the transaction at the start
        return a Tx object
        '''
        # s.read(n) will return n bytes
        # version is an integer in 4 bytes, little-endian
        version = little_endian_to_int(s.read(4))
        # num_inputs is a varint, use read_varint(s)
        num_inputs = read_varint(s)
        # parse num_inputs number of TxIns
        inputs = []
        for _ in range(num_inputs):
            inputs.append(TxIn.parse(s))
        # num_outputs is a varint, use read_varint(s)
        num_outputs = read_varint(s)
        # parse num_outputs number of TxOuts
        outputs = []
        for _ in range(num_outputs):
            outputs.append(TxOut.parse(s))
        # locktime is an integer in 4 bytes, little-endian
        locktime = little_endian_to_int(s.read(4))
        # return an instance of the class (see __init__ for args)
        return cls(version, inputs, outputs, locktime, testnet=testnet, segwit=False)

    @classmethod
    def parse_segwit(cls, s, testnet=False):
        print("in parse segwit")
        '''Takes a byte stream and parses the transaction at the start
        return a Tx object as a Segwit Tx having Segwit Flag '01'
        '''
        # s.read(n) will return n bytes
        # version is an integer in 4 bytes, little-endian
        version = little_endian_to_int(s.read(4))
        marker = s.read(2)
        if marker != b'\x00\x01':
            raise RuntimeError('not a segwit Flag 01 trasnaction {}'.format(marker))

        # num_inputs is a varint, use read_varint(s)
        num_inputs = read_varint(s)
        # parse num_inputs number of TxIns
        inputs = []
        for _ in range(num_inputs):
            inputs.append(TxIn.parse(s))
        # num_outputs is a varint, use read_varint(s)
        num_outputs = read_varint(s)
        # parse num_outputs number of TxOuts
        outputs = []
        for _ in range(num_outputs):
            outputs.append(TxOut.parse(s))
        # parse the witness field-one witness field for each tx_in
        for tx_in in inputs:
            print("in the tx_in witness parse")
            num_items = read_varint(s)
            items =[]
            for _ in range(num_items):
                item_len = read_varint(s)
                if item_len == 0:
                    items.append(0)
                    print("appendng 0")
                else:
                    items.append(s.read(item_len))
                    print("appending bytes")
            tx_in.witness = items
            print("ending tx_in witness parse")
        # locktime is an integer in 4 bytes, little-endian
        locktime = little_endian_to_int(s.read(4))
        # return an instance of the class (see __init__ for args)
        return cls(version, inputs, outputs, locktime, testnet=testnet, segwit=True)

    def serialize(self):
        if self.segwit:
            return self.serialize_segwit()
        else:
            return self.serialize_legacy()
    
    def serialize_legacy(self):
        '''Returns the byte serialization of the transaction'''
        # serialize version (4 bytes, little endian)
        result = int_to_little_endian(self.version, 4)
        # encode_varint on the number of inputs
        result += encode_varint(len(self.tx_ins))
        # iterate inputs
        for tx_in in self.tx_ins:
            # serialize each input
            result += tx_in.serialize()
        # encode_varint on the number of outputs
        result += encode_varint(len(self.tx_outs))
        # iterate outputs
        for tx_out in self.tx_outs:
            # serialize each output
            result += tx_out.serialize()
        # serialize locktime (4 bytes, little endian)
        result += int_to_little_endian(self.locktime, 4)
        return result

    def serialize_segwit(self):
        '''Returns the byte serialization of the transaction'''
        # serialize version (4 bytes, little endian)
        result = int_to_little_endian(self.version, 4)
        # serialize the Segwit Marker and Flag for 0x0001
        result += b'\x00\x01'
        # encode_varint on the number of inputs
        result += encode_varint(len(self.tx_ins))
        # iterate inputs
        for tx_in in self.tx_ins:
            # serialize each input
            result += tx_in.serialize()
        # encode_varint on the number of outputs
        result += encode_varint(len(self.tx_outs))
        # iterate outputs
        for tx_out in self.tx_outs:
            # serialize each output
            result += tx_out.serialize()

        # serialise the wtiness field
        for tx_in in self.tx_ins:
            #  tx_in_witness_len is the number of elements in the tx_in 
            #  witness field.
            tx_in_witness_len = len(tx_in.witness)
            #  encoding the length of the tx_in.witness to little endian
            #  result += int_to_little_endian(tx_in_witness_len, 1)
            #  but in the parse--the tx_in.witness length
            #  is parsed as a varint and bitcoin.org and segwit github
            #  says the number of items in the witness field is a varint
            #
            result += encode_varint(tx_in_witness_len)
            #
            for item in tx_in.witness:
                # Witness field is an array, composed of either integers or bytes
                # These seem like script, but segwit github expressly says the witness 
                # field is not script.

                # This if statement suggests some logic in the witness field array
                # instead of it just being an array of bytes.  Ultimately, that is 
                # what the witness field seems to be but putting in some logic now
                # as it potentially being an integer depends on how the witness filed 
                # items are dealt with--probably in the script eval portion--that
                # building a stack with witenss items--those have to be interpreted somehow.
                # The "else" part below is the only thing needed if the witenss field doesn't 
                # have any logic at this point--that its just an array of bytes.

                if type(item) == int:
                    #result += int_to_little_endian(item,1)
                    # The above is Jimmy Song's serialization
                    # But in the parse method, for each witness field input
                    # you first parse the fields length as a varint.
                    # Then you parse that varint number of bytes as the field element.
                    # So when serializing, it would seem that you need to first include
                    # the length of the witness item, even if it is an integer
                    int_byte = int_to_little_endian(item,1)
                    result += encode_varint(len(int_byte)) + int_byte
                else:
                    result += encode_varint(len(item)) + item

        # serialize locktime (4 bytes, little endian)
        result += int_to_little_endian(self.locktime, 4)
        return result

    # tag::source1[]
    def fee(self):
        '''Returns the fee of this transaction in satoshi'''
        input_sum, output_sum = 0, 0
        for tx_in in self.tx_ins:
            input_sum += tx_in.value(self.testnet)
        for tx_out in self.tx_outs:
            output_sum += tx_out.amount
        return input_sum - output_sum
    # end::source1[]

    def sig_hash(self, input_index, redeem_script=None):
        '''Returns the integer representation of the hash that needs to get
        signed for index input_index
        # start the serialization with version
        # use int_to_little_endian in 4 bytes
        # add how many inputs there are using encode_varint
        # loop through each input using enumerate, so we have the input index
            # if the input index is the one we're signing
            # the previous tx's ScriptPubkey is the ScriptSig
            # Otherwise, the ScriptSig is empty
            # add the serialization of the input with the ScriptSig we want
        # add how many outputs there are using encode_varint
        # add the serialization of each output
        # add the locktime using int_to_little_endian in 4 bytes
        # add SIGHASH_ALL using int_to_little_endian in 4 bytes
        # hash256 the serialization
        # convert the result to an integer using int.from_bytes(x, 'big')
        ''' 
        modified_tx = copy.deepcopy(self)
        for i in range(len(modified_tx.tx_ins)):  
            if i == input_index:
                # if the input being signed is p2sh:
                if redeem_script:
                    modified_tx.tx_ins[i].script_sig = redeem_script 
                # if not p2sh then assuming p2pkh      
                else:
                    # fetch the input transaction specified in the txi and get the script public key--a Script object
                    modified_tx.tx_ins[i].script_sig = modified_tx.tx_ins[i].script_pubkey(testnet = self.testnet)         
            else:
                modified_tx.tx_ins[i].script_sig = Script()

        modified_tx_serialized = modified_tx.serialize()
        # Assuming SIGHASS_ALL
        modified_tx_serialized += int_to_little_endian(1,4)
        print(modified_tx_serialized)
        z = hash256(modified_tx_serialized)
        
        z = int.from_bytes(z, 'big')
            
        return z


    def hash_prevouts(self):
        if self._hash_prevouts is None:
            all_prevouts = b''
            all_sequence = b''
            for tx_in in self.tx_ins:
                all_prevouts += tx_in.prev_tx[::-1] + int_to_little_endian(tx_in.prev_index, 4)
                all_sequence += int_to_little_endian(tx_in.sequence, 4)
            self._hash_prevouts = hash256(all_prevouts)
            self._hash_sequence = hash256(all_sequence)
        return self._hash_prevouts

    def hash_sequence(self):
        if self._hash_sequence is None:
            self.hash_prevouts()  # this should calculate self._hash_prevouts
        return self._hash_sequence

    def hash_outputs(self):
        if self._hash_outputs is None:
            all_outputs = b''
            for tx_out in self.tx_outs:
                all_outputs += tx_out.serialize()
            self._hash_outputs = hash256(all_outputs)
        return self._hash_outputs

    def sig_hash_bip143(self, input_index, redeem_script=None, witness_script=None):
        '''Returns the integer representation of the hash that needs to get
        signed for index input_index'''
        tx_in = self.tx_ins[input_index]
        print("****** in sig_hash_bip143")
        # per BIP143 spec
        s = int_to_little_endian(self.version, 4)  # applicable to all tx_ins in this tx
        s += self.hash_prevouts() + self.hash_sequence() # applicable to all tx_ins in this tx
        s += tx_in.prev_tx[::-1] + int_to_little_endian(tx_in.prev_index, 4)  # specific to this tx_in
        #
        # Setting the script_code:
        #
        # If there is a witness_script, then the situation is either a p2wsh
        # or a p2sh-p2wsh.  Use the witnesss script to make the script_code:
        if witness_script:
            script_code = witness_script.serialize()
        # If there is a redeem_script, then the situation is a p2sh-p2wpkh.
        # Make the script_code from the hash in the redeem_script-which is the 
        # 20-byte public key hash.
        elif redeem_script:
            script_code = p2pkh_script(redeem_script.cmds[1]).serialize()
        # If no witness_script or redeem_script, the situation is a straight
        # p2wpkh.  Use the 20 byte hash from the utxo script_pubkey.
        else:
            script_code = p2pkh_script(tx_in.script_pubkey(self.testnet).cmds[1]).serialize()
        s += script_code  # specific to this tx_ins
        s += int_to_little_endian(tx_in.value(), 8)  # specific to this tx_ins
        s += int_to_little_endian(tx_in.sequence, 4)  # specific to this tx_ins
        s += self.hash_outputs()  # applicable to all tx_ins in this tx
        s += int_to_little_endian(self.locktime, 4)  # applicable to all tx_ins in this tx
        s += int_to_little_endian(SIGHASH_ALL, 4) # applicable to all tx_ins in this tx
        print("****** out sig_hash_bip143")
        return int.from_bytes(hash256(s), 'big')
            

    def verify_input(self, input_index):
        '''Returns whether the input has a valid signature'''
        # get the relevant transaction input
        txi = self.tx_ins[input_index]
        
        # grab the previous (utxo) ScriptPubKey--"fetch's the utxo's script_pubkey"
        prev_script_pubkey = txi.script_pubkey(testnet = self.testnet)
        # is the script_pubkey a p2sh?
        if prev_script_pubkey.is_p2sh_script_pubkey():
            print("p2sh")
            # get the redeem script--the last element in the script_sig cmds list
            redeem_script_command = txi.script_sig.cmds[-1]
            # prepend the redeem_script_bytes with its length
            redeem_script_serialized = encode_varint(len(redeem_script_command)) + redeem_script_command
            
            # create the redeem_script as a script object
            redeem_script = Script.parse(BytesIO(redeem_script_serialized))
            if redeem_script.is_p2wpkh_script_pubkey():
                z = self.sig_hash_bip143(input_index, redeem_script)
                witness = txi.witness
            elif redeem_script.is_p2wsh_script_pubkey():
                cmd = txi.witness[-1]
                raw_witness = encode_varint(len(cmd)) + cmd
                witness_script = Script.parse(BytesIO(raw_witness))
                z = self.sig_hash_bip143(input_index, witness_script=witness_script)
                witness = txi.witness
            else:
                z = self.sig_hash(input_index = input_index, redeem_script = redeem_script)
                witness = None
        
        else: 
            if prev_script_pubkey.is_p2wpkh_script_pubkey():
                print("p2wpkh")
                z= self.sig_hash_bip143(input_index)
                witness = txi.witness
                print("witness: ")
                print(txi.witness)
            elif prev_script_pubkey.is_p2wsh_script_pubkey():
                print("p2wsh")
                cmd = txi.witness[-1]
                raw_witness = encode_varint(len(cmd)) + cmd 
                witness_script = Script.parse(BytesIO(raw_witness))
                z = self.sig_hash_bip143(input_index, witness_script=witness_script)
                witness = txi.witness
            else:
                z = self.sig_hash(input_index)
                print("else")
                witness = None

        # combine the current ScriptSig and the previous ScriptPubKey
        combined_script = txi.script_sig + prev_script_pubkey
        # evaluate the combined script
        print("in verify_input:  ")
        print(witness)
        verified = combined_script.evaluate(z, witness)
        print("in verify_input:  ")
        print(verified)
        return verified
    # tag::source2[]

    def verify(self):
        '''Verify this transaction'''
        if self.fee() < 0:  # <1>
            return False
        for i in range(len(self.tx_ins)):
            if not self.verify_input(i):  # <2>
                return False
        return True
    # end::source2[]

    def sign_input(self, input_index, private_key):
        # get the signature hash (z)

##
## Might need to provide logic to get sig_hash depending on whether it is segwit or not.
## The following right now is for not segwit
##

##  If spending a segwit utxo then --will need to look at the form of the utxo script pubkey
##      z = self.sig_hash_bip143
##  else 

        z = self.sig_hash(input_index)



        # get der signature of z from private key
        der = private_key.sign(z).der()
        # append the SIGHASH_ALL to der (use SIGHASH_ALL.to_bytes(1, 'big'))
        sig = der + SIGHASH_ALL.to_bytes(1,'big')
        # calculate the sec
        sec = private_key.point.sec()
        # initialize a new script with [sig, sec] as the cmds
        script = Script([sig, sec])
        print("Script_Sig from within sign_input:  ", script)
        # change input's script_sig to new script
        self.tx_ins[input_index].script_sig = script
        # return whether sig is valid using self.verify_input
        # verify_input will return True if the signautre is valid
        verify = self.verify_input(input_index)
        print(verify)
        return verify
           
        #raise NotImplementedError

    def sign_all_inputs(self, utxo_array):
        #private_key in the tx.sign_input is a private_key object
        for i in range(len(self.tx_ins)):
            private_key = PrivateKey(utxo_array[i].private_key)
            self.sign_input(input_index = i, private_key=private_key)

    def is_coinbase(self):
        '''Returns whether this transaction is a coinbase transaction or not'''
        # check that there is exactly 1 input
        if len(self.tx_ins) != 1:
            return False
        if self.tx_ins[0].prev_tx != int_to_little_endian(0, 32):
            return False
        # grab the first input
        # check that first input prev_tx is b'\x00' * 32 bytes
        
        # check that first input prev_index is 0xffffffff
        if self.tx_ins[0].prev_index != 0xffffffff:
            return False
        return True


    def coinbase_height(self):
        if self.is_coinbase():
            cmd = self.tx_ins[0].script_sig.cmds[0]
            height = little_endian_to_int(cmd)
            return height
        else:
            return None
class TxIn:
    # prev_tx in bytes
    # prev_index as integer
    def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xffffffff, witness=None):
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        if script_sig is None:
            self.script_sig = Script()
        else:
            self.script_sig = script_sig
        self.sequence = sequence

        # Allow for the witness field
        self.witness = witness

    def __repr__(self):
        return '{}:{}:{}:{}:{}'.format(
            self.prev_tx.hex(),
            self.prev_index,
            self.script_sig,
            self.sequence,
            self.witness
        )

    @classmethod
    def parse(cls, s):
        '''Takes a byte stream and parses the tx_input at the start
        return a TxIn object
        '''
        # prev_tx is 32 bytes, little endian
        prev_tx = s.read(32)[::-1]
        # prev_index is an integer in 4 bytes, little endian
        prev_index = little_endian_to_int(s.read(4))
        # use Script.parse to get the ScriptSig
        script_sig = Script.parse(s)
        # sequence is an integer in 4 bytes, little-endian
        sequence = little_endian_to_int(s.read(4))
        # return an instance of the class (see __init__ for args)
        return cls(prev_tx, prev_index, script_sig, sequence)

    def serialize(self):
        '''Returns the byte serialization of the transaction input'''
        # serialize prev_tx, little endian
        result = self.prev_tx[::-1]
        # serialize prev_index, 4 bytes, little endian
        result += int_to_little_endian(self.prev_index, 4)
        # serialize the script_sig
        result += self.script_sig.serialize()
        # serialize sequence, 4 bytes, little endian
        result += int_to_little_endian(self.sequence, 4)
        return result

    def fetch_tx(self, testnet=False):
        return TxFetcher.fetch(self.prev_tx.hex(), testnet=testnet)

    def value(self, testnet=False):
        '''Get the outpoint value by looking up the tx hash
        Returns the amount in satoshi
        '''
        # use self.fetch_tx to get the transaction
        tx = self.fetch_tx(testnet=testnet)
        # get the output at self.prev_index
        # return the amount property
        return tx.tx_outs[self.prev_index].amount

    def script_pubkey(self, testnet=False):
        '''Get the ScriptPubKey by looking up the tx hash
        Returns a Script object
        '''
        # use self.fetch_tx to get the transaction
        tx = self.fetch_tx(testnet=testnet)
        # get the output at self.prev_index
        # return the script_pubkey property
        return tx.tx_outs[self.prev_index].script_pubkey


class TxOut:

    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey

    def __repr__(self):
        return '{}:{}'.format(self.amount, self.script_pubkey)

    @classmethod
    def parse(cls, s):
        '''Takes a byte stream and parses the tx_output at the start
        return a TxOut object
        '''
        # amount is an integer in 8 bytes, little endian
        amount = little_endian_to_int(s.read(8))
        # use Script.parse to get the ScriptPubKey
        script_pubkey = Script.parse(s)
        # return an instance of the class (see __init__ for args)
        return cls(amount, script_pubkey)

    @classmethod
    def output_from_address(cls, address, amount):
    # creates an output from the Base 58 Checksum string
    # the Base 58 Checksum string is what a payor would receive from the payee
        hash160_bytes = decode_base58(address)
        script_pub_key = p2pkh_script(hash160_bytes)
        return cls(amount, script_pub_key)





    def serialize(self):
        '''Returns the byte serialization of the transaction output'''
        # serialize amount, 8 bytes, little endian
        result = int_to_little_endian(self.amount, 8)
        # serialize the script_pubkey
        result += self.script_pubkey.serialize()
        return result
    
    


class TxTest(TestCase):
    cache_file = '../tx.cache'

    @classmethod
    def setUpClass(cls):
        # fill with cache so we don't have to be online to run these tests
        TxFetcher.load_cache(cls.cache_file)

    def test_parse_version(self):
        raw_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.version, 1)

    def test_parse_inputs(self):
        raw_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(len(tx.tx_ins), 1)
        want = bytes.fromhex('d1c789a9c60383bf715f3f6ad9d14b91fe55f3deb369fe5d9280cb1a01793f81')
        self.assertEqual(tx.tx_ins[0].prev_tx, want)
        self.assertEqual(tx.tx_ins[0].prev_index, 0)
        want = bytes.fromhex('6b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278a')
        self.assertEqual(tx.tx_ins[0].script_sig.serialize(), want)
        self.assertEqual(tx.tx_ins[0].sequence, 0xfffffffe)

    def test_parse_outputs(self):
        raw_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(len(tx.tx_outs), 2)
        want = 32454049
        self.assertEqual(tx.tx_outs[0].amount, want)
        want = bytes.fromhex('1976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac')
        self.assertEqual(tx.tx_outs[0].script_pubkey.serialize(), want)
        want = 10011545
        self.assertEqual(tx.tx_outs[1].amount, want)
        want = bytes.fromhex('1976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac')
        self.assertEqual(tx.tx_outs[1].script_pubkey.serialize(), want)

    def test_parse_locktime(self):
        raw_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.locktime, 410393)

    def test_serialize(self):
        raw_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.serialize(), raw_tx)

    def test_input_value(self):
        tx_hash = 'd1c789a9c60383bf715f3f6ad9d14b91fe55f3deb369fe5d9280cb1a01793f81'
        index = 0
        want = 42505594
        tx_in = TxIn(bytes.fromhex(tx_hash), index)
        self.assertEqual(tx_in.value(), want)

    def test_input_pubkey(self):
        tx_hash = 'd1c789a9c60383bf715f3f6ad9d14b91fe55f3deb369fe5d9280cb1a01793f81'
        index = 0
        tx_in = TxIn(bytes.fromhex(tx_hash), index)
        want = bytes.fromhex('1976a914a802fc56c704ce87c42d7c92eb75e7896bdc41ae88ac')
        self.assertEqual(tx_in.script_pubkey().serialize(), want)

    def test_fee(self):
        raw_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.fee(), 40000)
        raw_tx = bytes.fromhex('010000000456919960ac691763688d3d3bcea9ad6ecaf875df5339e148a1fc61c6ed7a069e010000006a47304402204585bcdef85e6b1c6af5c2669d4830ff86e42dd205c0e089bc2a821657e951c002201024a10366077f87d6bce1f7100ad8cfa8a064b39d4e8fe4ea13a7b71aa8180f012102f0da57e85eec2934a82a585ea337ce2f4998b50ae699dd79f5880e253dafafb7feffffffeb8f51f4038dc17e6313cf831d4f02281c2a468bde0fafd37f1bf882729e7fd3000000006a47304402207899531a52d59a6de200179928ca900254a36b8dff8bb75f5f5d71b1cdc26125022008b422690b8461cb52c3cc30330b23d574351872b7c361e9aae3649071c1a7160121035d5c93d9ac96881f19ba1f686f15f009ded7c62efe85a872e6a19b43c15a2937feffffff567bf40595119d1bb8a3037c356efd56170b64cbcc160fb028fa10704b45d775000000006a47304402204c7c7818424c7f7911da6cddc59655a70af1cb5eaf17c69dadbfc74ffa0b662f02207599e08bc8023693ad4e9527dc42c34210f7a7d1d1ddfc8492b654a11e7620a0012102158b46fbdff65d0172b7989aec8850aa0dae49abfb84c81ae6e5b251a58ace5cfeffffffd63a5e6c16e620f86f375925b21cabaf736c779f88fd04dcad51d26690f7f345010000006a47304402200633ea0d3314bea0d95b3cd8dadb2ef79ea8331ffe1e61f762c0f6daea0fabde022029f23b3e9c30f080446150b23852028751635dcee2be669c2a1686a4b5edf304012103ffd6f4a67e94aba353a00882e563ff2722eb4cff0ad6006e86ee20dfe7520d55feffffff0251430f00000000001976a914ab0c0b2e98b1ab6dbf67d4750b0a56244948a87988ac005a6202000000001976a9143c82d7df364eb6c75be8c80df2b3eda8db57397088ac46430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.fee(), 140500)

    def test_sig_hash(self):
        #  From BlockCypher
        #tx = TxFetcher.fetch('07740fe2068c5582919c9dbbce042b73aeb9cbe7667d4805c40619bb6659b5d0')
        #  From Bitcoing Programming
        tx = TxFetcher.fetch('452c629d67e41baec3ac6f04fe744b4b9617f8f859c63b3002f8684e7a4fee03')
        want = int('27e0c5994dec7824e56dec6b2fcb342eb7cdb0d0957c2fce9882f715e85d81a6', 16)
        self.assertEqual(tx.sig_hash(0), want)

    def test_verify_p2pkh(self):
        tx = TxFetcher.fetch('452c629d67e41baec3ac6f04fe744b4b9617f8f859c63b3002f8684e7a4fee03')
        self.assertTrue(tx.verify())
        tx = TxFetcher.fetch('5418099cc755cb9dd3ebc6cf1a7888ad53a1a3beb5a025bce89eb1bf7f1650a2', testnet=True)
        self.assertTrue(tx.verify())

    def test_verify_p2sh(self):
        tx = TxFetcher.fetch('46df1a9484d0a81d03ce0ee543ab6e1a23ed06175c104a178268fad381216c2b')
        self.assertTrue(tx.verify())

    def test_sign_input(self):
        private_key = PrivateKey(secret=8675309)
        stream = BytesIO(bytes.fromhex('010000000199a24308080ab26e6fb65c4eccfadf76749bb5bfa8cb08f291320b3c21e56f0d0d00000000ffffffff02408af701000000001976a914d52ad7ca9b3d096a38e752c2018e6fbc40cdf26f88ac80969800000000001976a914507b27411ccf7f16f10297de6cef3f291623eddf88ac00000000'))
        tx_obj = Tx.parse(stream, testnet=True)
        self.assertTrue(tx_obj.sign_input(0, private_key))
        want = '010000000199a24308080ab26e6fb65c4eccfadf76749bb5bfa8cb08f291320b3c21e56f0d0d0000006b4830450221008ed46aa2cf12d6d81065bfabe903670165b538f65ee9a3385e6327d80c66d3b502203124f804410527497329ec4715e18558082d489b218677bd029e7fa306a72236012103935581e52c354cd2f484fe8ed83af7a3097005b2f9c60bff71d35bd795f54b67ffffffff02408af701000000001976a914d52ad7ca9b3d096a38e752c2018e6fbc40cdf26f88ac80969800000000001976a914507b27411ccf7f16f10297de6cef3f291623eddf88ac00000000'
        self.assertEqual(tx_obj.serialize().hex(), want)

    def test_is_coinbase(self):
        raw_tx = bytes.fromhex('01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff5e03d71b07254d696e656420627920416e74506f6f6c20626a31312f4542312f4144362f43205914293101fabe6d6d678e2c8c34afc36896e7d9402824ed38e856676ee94bfdb0c6c4bcd8b2e5666a0400000000000000c7270000a5e00e00ffffffff01faf20b58000000001976a914338c84849423992471bffb1a54a8d9b1d69dc28a88ac00000000')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertTrue(tx.is_coinbase())

    def test_coinbase_height(self):
        raw_tx = bytes.fromhex('01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff5e03d71b07254d696e656420627920416e74506f6f6c20626a31312f4542312f4144362f43205914293101fabe6d6d678e2c8c34afc36896e7d9402824ed38e856676ee94bfdb0c6c4bcd8b2e5666a0400000000000000c7270000a5e00e00ffffffff01faf20b58000000001976a914338c84849423992471bffb1a54a8d9b1d69dc28a88ac00000000')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.coinbase_height(), 465879)
        raw_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertIsNone(tx.coinbase_height())