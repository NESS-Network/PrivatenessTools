from NessKeys.interfaces.Cryptor import Cryptor
from Crypto.Cipher import AES as AES
from Crypto.Random import get_random_bytes
from base64 import b64encode
from base64 import b64decode
import json

class Aes(Cryptor):

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        header = get_random_bytes(16)

        cipher = AES.new(key, AES.MODE_GCM)
        cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        return header + cipher.nonce + tag + ciphertext

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        header = data[:16]
        nonce = data[16:32]
        tag = data[32:48]
        ciphertext = data[48:]

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        cipher.update(header)

        return cipher.decrypt_and_verify(ciphertext, tag)

    def getCipher(self) -> str:
        return 'aes'

    def getBlockSize(self) -> int:
        return 16

    def getBlockAddition(self) -> int:
        return 48