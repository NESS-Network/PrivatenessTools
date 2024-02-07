from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException
from ..interfaces.NessKey import NessKey
import json

class BlockchainRPC(NessKey):

    def load(self, keydata: dict):
        map = {
            "filedata": {
                "vendor": "Privateness",
                "type": "config",
                "for": "blockchain"
            },
            "rpc-host": str,
            "rpc-port": int,
            "rpc-user": str,
            "rpc-password": str,
        }

        JsonChecker.check('Backup key check', keydata, map)

        self.__host = keydata["rpc-host"]
        self.__port = keydata["rpc-port"]
        self.__user = keydata["rpc-user"]
        self.__password = keydata["rpc-password"]

    def compile(self) -> dict:
        appdata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "config",
                "for": "blockchain"
            },
            "rpc-host": self.__host,
            "rpc-port": self.__port,
            "rpc-user": self.__user,
            "rpc-password": self.__password,
        }

        return appdata

    def serialize(self) -> str:
        return json.dumps(self.compile())

    def worm(self) -> str:
        return ""
        
    def nvs(self) -> str:
        return ""

    def print(self):
        return "Privateness Blockchain Config"

    def filename():
        return "blockchain-rpc.json"

    def getFilename(self):
        return BlockchainRPC.filename()

    def getHost(self) -> str:
        return self.__host

    def getPort(self) -> str:
        return self.__port

    def getUser(self) -> str:
        return self.__user

    def getPassword(self) -> str:
        return self.__password
