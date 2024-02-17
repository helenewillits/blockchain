# Description:
# Defines users and handles their data.

import hashlib
import nacl.utils
from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder

import binascii


class User:
    def __init__(self):
        self.__private_key = SigningKey.generate()
        self.public_key = self.__private_key.verify_key

    # signing functions
    def sign(self, message):
        message = bytes(message, 'utf-8')
        return self.__private_key.sign(message, encoder=HexEncoder).decode("utf-8")

    def verify_signature(public_key, signature):
        signature = signature.encode("utf-8")
        if type(public_key) != nacl.signing.VerifyKey:
            verify_key = User.get_deserialized_public_key(public_key) 
        # raises nacl.exceptions.BadSignatureError if it fails
        return verify_key.verify(signature, encoder=HexEncoder)

    def get_serialized_public_key(public_key):
        return public_key.encode(encoder=HexEncoder).decode("utf-8")

    def get_deserialized_public_key(public_key):
        return VerifyKey(public_key, encoder=HexEncoder)