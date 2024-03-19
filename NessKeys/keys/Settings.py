from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException
from ..interfaces.NessKey import NessKey
import json

class Settings(NessKey):
    __entrophy = 100
    __cipher = "salsa20"

    def load(self, keydata: dict):
        map = {
            "filedata": {
                "vendor": "Privateness",
                "type": "settings",
                "for": "settings"
            },
            "entrophy": int,
            "cipher": str,
        }

        JsonChecker.check('Settings key check', keydata, map)

        self.__entrophy = keydata["entrophy"]
        self.__cipher = keydata["cipher"]
    
    def compile(self) -> dict:
        return {
            "filedata": {
                "vendor": "Privateness",
                "type": "settings",
                "for": "settings"
            },
            "entrophy": self.__entrophy,
            "cipher": self.__cipher
        }

    def serialize(self) -> str:
        return json.dumps(self.compile())

    def print(self):
        return "Privateness settings"

    def filename():
        return "settings.json"

    def getFilename(self):
        return "settings.json"
    
    def worm(self):
        return ''
    
    def nvs(self):
        return ''

    def getEntrophy(self):
        if self.__entrophy < 10:
            self.__entrophy = 10

        return self.__entrophy

    def getCipher(self):
        self.__cipher = self.__cipher.lower()

        if self.__cipher != 'salsa20' and self.__cipher != 'aes':
            self.__cipher = 'salsa20'

        return self.__cipher

    def setKey(self, entrophy: int):
        self.__entrophy = entrophy

    def setCipher(self, cipher: str):
        self.__cipher = cipher