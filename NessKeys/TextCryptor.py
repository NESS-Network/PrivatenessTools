from NessKeys.exceptions.CrcCheck import CrcCheck
from NessKeys.interfaces.Cryptor import Cryptor
from Crypto.Hash import SHA256
from base64 import b64encode
from base64 import b64decode

class TextCryptor:
    def __init__(self, cryptor: Cryptor, key: bytes):
        self.cryptor = cryptor
        self.key = key

    def encrypt(self, data: bytes) -> bytes:
        return self.cryptor.encrypt(data, self.key)

    def decrypt(self, data: bytes) -> bytes:
        return self.cryptor.decrypt(data, self.key)