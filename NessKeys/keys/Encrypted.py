from NessKeys.interfaces.NessKey import NessKey
from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException

class Encrypted(NessKey):

    def load(self, keydata: dict):
        map = {
            "filedata": {
                "vendor": "Privateness",
                "type": "encrypted-keys",
                "for": str,
                "cipher": str
            },
            "keys": list,
            "crc": list
        }

        JsonChecker.check('Directories', keydata, map)


        self.__for = keydata["filedata"]["for"]
        self.__cipher = keydata["filedata"]["cipher"]
        self.__keys = keydata["keys"]
        self.__crc = keydata["crc"]

    def compile(self) -> dict:
        appdata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "encrypted-keys",
                "for": self.__for,
                "cipher": self.__cipher
            },
            "keys": self.__keys,
            "crc": self.__crc
        }
        
        return appdata

    def worm(self) -> str:
        return ""
        
    def nvs(self) -> str:
        return ""
        
    def print(self):
        return "Privateness Encrypted Key Storage for {}\nKeys count: {}\nCipher: {}".format(self.__for, len(self.__keys), self.__cipher)

    def getFilename(self):
        return "encrypted.keys.json"

    def getKeys(self):
        return self.__keys

    def setKeys(self, keys: list):
        self.__keys = keys

    def getCrc(self):
        return self.__crc

    def setCrc(self, crc: list):
        self.__crc = crc

    def addKey(self, key: str):
        self.__keys.append(key)

    def getCipher(self):
        return self.__cipher