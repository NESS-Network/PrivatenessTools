from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException
from ..interfaces.NessKey import NessKey
import json

class Backup(NessKey):

    def load(self, keydata: dict):
        map = {
            "filedata": {
                "vendor": "Privateness",
                "type": "backup",
                "for": "backup"
            },
            "seed": str,
            "key": str
        }

        JsonChecker.check('Backup key check', keydata, map)

        self.__seed = keydata["seed"]
        self.__key = keydata["key"]
    
    def compile(self) -> dict:
        return {
            "filedata": {
                "vendor": "Privateness",
                "type": "backup",
                "for": "backup"
            },
            "seed": self.__seed,
            "key": self.__key
        }

    def serialize(self) -> str:
        return json.dumps(self.compile())

    def print(self):
        return "Privateness backup"

    def getFilename(self):
        return "backup.json"
    
    def worm(self):
        return ''
    
    def nvs(self):
        return ''

    def getSeed(self):
        return self.__seed

    def getKey(self):
        return self.__key