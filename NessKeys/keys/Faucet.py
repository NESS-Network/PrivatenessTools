from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException
from ..interfaces.NessKey import NessKey
import json
import urllib.parse

class Faucet(NessKey):

    def load(self, keydata: dict):
        map = {
            "filedata": {
                "vendor": "Privateness",
                "type": "key",
                "for": "faucet"
            },
            "keys": {
                "private": str,
                "verify": str
            },
            "url": str
        }

        JsonChecker.check('Faucet key check', keydata, map)

        self.__private_key = keydata["keys"]["private"]
        self.__verify_key = keydata["keys"]["verify"]
        self.__url = keydata["url"]

    def compile(self) -> dict:
        nodedata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "key",
                "for": "faucet"
            },
            "keys": {
                "private": self.__private_key,
                "verify": self.__verify_key
            },
            "url": self.__url
        }

        nodedata["worm"] = self.__wrm(nodedata)

        return nodedata

    def serialize(self) -> str:
        return json.dumps(self.compile())

    def worm(self) -> str:
        nodedata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "key",
                "for": "faucet"
            },
            "keys": {
                "private": self.__private_key,
                "verify": self.__verify_key
            },
            "url": self.__url
        }

        return self.__wrm(nodedata)
        
    def nvs(self) -> str:
        return "worm:faucet:ness:" + self.__url
        
    def print(self):
        return "Privateness Faucet Key: <{}>".format(self.__url)

    def getFilename(self):
        return urllib.parse.quote_plus(self.__url) + ".key.json"

    def __wrm(self, nodedata: dict):
        linesep = '\n'
        tab = '\t'
        tab2 = '\t\t'

        worm = "<worm>" + linesep + \
            tab + "<faucet type=\"ness\" url=\"" + nodedata["url"] + "\">" + linesep + \
            tab2 + "<!-- Description here -->" + linesep + \
            tab + "</faucet>" + linesep + \
            "</worm>"

        return worm

    def getPrivateKey(self):
        return self.__private_key

    def getVerifyKey(self):
        return self.__verify_key

    def getUrl(self):
        return self.__url