import NessKeys.interfaces.Cryptor as Cryptor
from NessKeys.cryptors.Salsa20 import Salsa20
from NessKeys.cryptors.Aes import Aes
from NessKeys.exceptions.CipherNotExist import CipherNotExist

class CryptorMaker:
    def make(cipher: str) -> Cryptor:
        if cipher == "salsa20":
            return Salsa20()
        elif cipher == "aes":
            return Aes()
        else:
            raise CipherNotExist(cipher) 