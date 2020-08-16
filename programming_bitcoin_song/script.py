from io import BytesIO
from logging import getLogger
from unittest import TestCase


from helper import (
    encode_varint,
    h160_to_p2pkh_address,
    h160_to_p2sh_address,
    int_to_little_endian,
    little_endian_to_int,
    read_varint,
    sha256
)
import op
from op import (
    OP_CODE_FUNCTIONS,
    OP_CODE_NAMES,
)


# tag::source1[]
def p2pkh_script(h160):
    '''Takes a hash160 and returns the p2pkh ScriptPubKey'''
    return Script([0x76, 0xa9, h160, 0x88, 0xac])
# end::source1[]

def p2sh_script(h160):
    '''Takes a hash160 and returns the p2sh ScriptPubKey'''
    return Script([0xa9, h160, 0x87])

def p2wpkh_script(h160):
    '''Takes a hash160 and returns the p2wpkh ScriptPubKey'''
    return Script([0x00, h160])

def p2wsh_script(h256):
    '''Takes a sha256--the hash of the witness script--and returns a p2wsh ScriptPubKey
       Remember:  the has is a sha256 NOT a hash256'''

    return Script([0x00, h256])

def redeem_script(n, pub_key_list, m):
    '''creates the redeem script 
        n: number of required signatures
        pub_key_list:  list of available public keys--!!! in what format? 
        m: number of availalbe public keys
    '''
    cmds = [n]
    cmds.extend(pub_key_list)
    cmds.append(m)
    cmds.append(0xae)
    return Script(cmds)

LOGGER = getLogger(__name__)


class Script:

    def __init__(self, cmds=None):
        if cmds is None:
            self.cmds = []
        else:
            self.cmds = cmds

    def __repr__(self):
        result = []
        for cmd in self.cmds:
            if type(cmd) == int:
                if OP_CODE_NAMES.get(cmd):
                    name = OP_CODE_NAMES.get(cmd)
                else:
                    name = 'OP_[{}]'.format(cmd)
                result.append(name)
            else:
                result.append(cmd.hex())
        return ' '.join(result)

    def __add__(self, other):
        return Script(self.cmds + other.cmds)

    @classmethod
    def parse(cls, s):
        # get the length of the entire field
        length = read_varint(s)
        # initialize the cmds array
        cmds = []
        # initialize the number of bytes we've read to 0
        count = 0
        # loop until we've read length bytes
        while count < length:
            # get the current byte
            current = s.read(1)
            # increment the bytes we've read
            count += 1
            # convert the current byte to an integer
            current_byte = current[0]
            # if the current byte is between 1 and 75 inclusive
            if current_byte >= 1 and current_byte <= 75:
                # we have an cmd set n to be the current byte
                n = current_byte
                # add the next n bytes as an cmd
                cmds.append(s.read(n))
                # increase the count by n
                count += n
            elif current_byte == 76:
                # op_pushdata1
                data_length = little_endian_to_int(s.read(1))
                cmds.append(s.read(data_length))
                count += data_length + 1
            elif current_byte == 77:
                # op_pushdata2
                data_length = little_endian_to_int(s.read(2))
                cmds.append(s.read(data_length))
                count += data_length + 2
            else:
                # we have an opcode. set the current byte to op_code
                op_code = current_byte
                # add the op_code to the list of cmds
                cmds.append(op_code)
        if count != length:
            
            raise SyntaxError('parsing script failed')
        return cls(cmds)

    def raw_serialize(self):
        # initialize what we'll send back
        result = b''
        # go through each cmd
        for cmd in self.cmds:
            # if the cmd is an integer, it's an opcode
            if type(cmd) == int:
                # turn the cmd into a single byte integer using int_to_little_endian
                result += int_to_little_endian(cmd, 1)
            else:
                # otherwise, this is an element
                # get the length in bytes
                length = len(cmd)
                # for large lengths, we have to use a pushdata opcode
                if length < 75:
                    # turn the length into a single byte integer
                    result += int_to_little_endian(length, 1)
                elif length > 75 and length < 0x100:
                    # 76 is pushdata1
                    result += int_to_little_endian(76, 1)
                    result += int_to_little_endian(length, 1)
                elif length >= 0x100 and length <= 520:
                    # 77 is pushdata2
                    result += int_to_little_endian(77, 1)
                    result += int_to_little_endian(length, 2)
                else:
                    raise ValueError('too long an cmd')
                result += cmd
        return result

    def serialize(self):
        # get the raw serialization (no prepended length)
        result = self.raw_serialize()
        # get the length of the whole thing
        total = len(result)
        # encode_varint the total length of the result and prepend
        return encode_varint(total) + result

    def evaluate(self, z, witness):
        # create a copy as we may need to add to this list if we have a
        # RedeemScript
        cmds = self.cmds[:]
        stack = []
        altstack = []
        while len(cmds) > 0:
            cmd = cmds.pop(0)
            if type(cmd) == int:
                # do what the opcode says
                # retrieving the function in op.py corresponding to the opcode
                operation = OP_CODE_FUNCTIONS[cmd]
                if cmd in (99, 100):
                    # op_if/op_notif require the cmds array
                    if not operation(stack, cmds):
                        LOGGER.info('bad op: {}'.format(OP_CODE_NAMES[cmd]))
                        return False
                elif cmd in (107, 108):
                    # op_toaltstack/op_fromaltstack require the altstack
                    if not operation(stack, altstack):
                        LOGGER.info('bad op: {}'.format(OP_CODE_NAMES[cmd]))
                        return False
                elif cmd in (172, 173, 174, 175):
                    # these are signing operations, they need a sig_hash
                    # to check against
                    if not operation(stack, z):
                        LOGGER.info('bad op: {}'.format(OP_CODE_NAMES[cmd]))
                        return False
                else:
                    if not operation(stack):
                        LOGGER.info('bad op: {}'.format(OP_CODE_NAMES[cmd]))
                        return False
            else:
                # add the cmd to the stack
                stack.append(cmd)
                # Determine whether this is a p2sh:
                # To do so, you need to look at the next three items in the command set.
                # Are there only three items remaining in the command set and are theY:
                # 0xa9 --op_hash160, 20 bytes--for the script hash and 0x87--op_equal?
                if len(cmds) == 3 and cmds[0] == 0xa9 and type(cmds[1]) == bytes and len(cmds[1]) == 20 and cmds[2] == 0x87:  # <1>
                    cmds.pop()  # <2>
                    h160 = cmds.pop()
                    cmds.pop()
                    if not op.op_hash160(stack):  # <3>
                        return False
                    stack.append(h160)
                    if not op.op_equal(stack):
                        return False
                    if not op.op_verify(stack):  # <4>
                        LOGGER.info('bad p2sh h160')
                        return False
                    redeem_script = encode_varint(len(cmd)) + cmd  # <5>
                    stream = BytesIO(redeem_script)
                    cmds.extend(Script.parse(stream).cmds)  # <6>
                # Determine whether this is a p2wpkh. 
                # To do so, you need to look at the stack (remember focus on the stack now, not the command set).
                # Are there only two items on the stack?  is the first b'' and the second 20 bytes?
                # The 20 bytes will be the hash of the witness field.
                # If so, then use the witness field and the hash on the stack to build a p2pkh command set.
                if len(stack) == 2 and stack[0] == b'' and len(stack[1]) == 20:
                    h160 = stack.pop()
                    stack.pop()
                    # witness should be two items, the signature and the public key (in bytes not BASE58)
                    cmds.extend(witness)
                    # the build out the command set with the p2pkh commands
                    cmds.extend(p2pkh_script(h160).cmds)
                    # now we have the p2pkh command set and the script evaluation proceeds...
                # Determine whether this is a p2wsh:
                # Does stack have just two items, b'' and a 32 byte hash-which hash is the witness script hash.
                # If so, check that the hash of the witness script equals the witness script hash 
                # that is already on the stack.  If so, build a command set starting with the witness filed items 
                # and then parse the witness script.  Append the parsed witness script items to the command set.
                # The p2wsh is often used for the segwit form of the m of n multisig.
                if len(stack) == 2 and stack[0] == b'' and type(stack[1]) == bytes and len(stack[1])==32:
                    s256 = stack.pop()
                    stack.pop()
                    witness_script = witness[-1]
                    if s256 != sha256(witness_script):
                        print('bad sha256 {} vs {}'.format(s256.hex(), sha256(witness_script).hex()))
                        return False
                    # If the wintess script checks out then add the witness fields to the command set--leaving the 
                    # witness script item to be parsed still
                    cmds.extend(witness[:-1])
                    # Parse the witness script--prepare it as a raw script and make into a stream first.
                    witness_script = encode_varint(len(witness_script)) + witness_script
                    witness_stream = BytesIO(witness_script)
                    witness_script_cmds = Script.parse(witness_stream).cmds
                    # Add the witness script items to the command set--these should be the script_pub_key
                    # items from a regular p2sh script_pub_key--which would be the m of n multisig.
                    cmds.extend(witness_script_cmds)

        if len(stack) == 0:
            return False
        if stack.pop() == b'':
            return False
        return True


    def is_p2pkh_script_pubkey(self):
        '''Returns whether this follows the
        OP_DUP OP_HASH160 <20 byte hash> OP_EQUALVERIFY OP_CHECKSIG pattern.'''
        return len(self.cmds) == 5 and self.cmds[0] == 0x76 \
            and self.cmds[1] == 0xa9 \
            and type(self.cmds[2]) == bytes and len(self.cmds[2]) == 20 \
            and self.cmds[3] == 0x88 and self.cmds[4] == 0xac

    def is_p2sh_script_pubkey(self):
        '''Returns whether this follows the
        OP_HASH160 <20 byte hash> OP_EQUAL pattern.'''
        return len(self.cmds) == 3 and self.cmds[0] == 0xa9 \
            and type(self.cmds[1]) == bytes and len(self.cmds[1]) == 20 \
            and self.cmds[2] == 0x87

    def is_p2wpkh_script_pubkey(self):
        return len(self.cmds) == 2 and self.cmds[0] == 0x00 and type(self.cmds[1]) == bytes and len(self.cmds[1]) == 20

    def is_p2wsh_script_pubkey(self):
        return len(self.cmds) ==2 and self.cmds[0] == 0x00 and type(self.cmds[1]) == bytes and len(self.cmds[1]) == 32

    def determine_script_pubkey_type(self):
        if self.is_p2pkh_script_pubkey():
            return("p2pkh")
        elif self.is_p2sh_script_pubkey():
            return("p2sh")
        elif self.is_p2sh_script_pubkey():
            return("p2sh")
        elif self.is_p2wpkh_script_pubkey():
            return("p2wpkh")
        elif self.is_p2wsh_script_pubkey():
            return("p2wsh")
        else:
            return("public key hash indetermined")
    


    def address(self, testnet=False):
        '''Returns the address corresponding to the script'''
        if self.is_p2pkh_script_pubkey():  # p2pkh
            # hash160 is the 3rd cmd
            h160 = self.cmds[2]
            # convert to p2pkh address using h160_to_p2pkh_address (remember testnet)
            return h160_to_p2pkh_address(h160, testnet)
        elif self.is_p2sh_script_pubkey():  # p2sh
            # hash160 is the 2nd cmd
            h160 = self.cmds[1]
            # convert to p2sh address using h160_to_p2sh_address (remember testnet)
            return h160_to_p2sh_address(h160, testnet)

class ScriptTest(TestCase):

    def test_parse(self):
        script_pubkey = BytesIO(bytes.fromhex('6a47304402207899531a52d59a6de200179928ca900254a36b8dff8bb75f5f5d71b1cdc26125022008b422690b8461cb52c3cc30330b23d574351872b7c361e9aae3649071c1a7160121035d5c93d9ac96881f19ba1f686f15f009ded7c62efe85a872e6a19b43c15a2937'))
        script = Script.parse(script_pubkey)
        want = bytes.fromhex('304402207899531a52d59a6de200179928ca900254a36b8dff8bb75f5f5d71b1cdc26125022008b422690b8461cb52c3cc30330b23d574351872b7c361e9aae3649071c1a71601')
        self.assertEqual(script.cmds[0].hex(), want.hex())
        want = bytes.fromhex('035d5c93d9ac96881f19ba1f686f15f009ded7c62efe85a872e6a19b43c15a2937')
        self.assertEqual(script.cmds[1], want)

    def test_serialize(self):
        want = '6a47304402207899531a52d59a6de200179928ca900254a36b8dff8bb75f5f5d71b1cdc26125022008b422690b8461cb52c3cc30330b23d574351872b7c361e9aae3649071c1a7160121035d5c93d9ac96881f19ba1f686f15f009ded7c62efe85a872e6a19b43c15a2937'
        script_pubkey = BytesIO(bytes.fromhex(want))
        script = Script.parse(script_pubkey)
        self.assertEqual(script.serialize().hex(), want)
