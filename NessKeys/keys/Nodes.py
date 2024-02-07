from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.DeepChecker import DeepChecker
from ..JsonChecker.KeyChecker import KeyChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException
from ..interfaces.NessKey import NessKey

class Nodes(NessKey):

    def load(self, keydata: dict):
        map = {
            "filedata": {
                "vendor": "Privateness",
                "type": "data",
                "for": "nodes-list"
            },
            "nodes": list
        }
        
        JsonChecker.check('Nodes key check', keydata, map)

        map = {
            "url": str,
            "public": str,
            "verify": str,
            "nonce": str,
            "master": str,
            "tariff": float,
            "tags": list
        }

        DeepChecker.check('Nodes key check (nodes list)', keydata['nodes'], map, 1)

        self.__nodes = keydata["nodes"]


    def compile(self) -> dict:
        appdata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "data",
                "for": "nodes-list"
            },
            "nodes": self.__nodes
        }

        return appdata

    def worm(self) -> str:
        return ""
        
    def nvs(self) -> str:
        return ""

    def print(self):
        return "Privateness Nodes storage file"

    def filename():
        return "nodes.json"

    def getFilename(self):
        return Nodes.filename()

    def getNodes(self) -> dict:
        return self.__nodes

    def setNodes(self, nodes: dict):
        self.__nodes = nodes

    def findNode(self, url: str) -> dict:
        for i in self.__nodes:
            if self.__nodes[i]['url'] == url:
                return self.__nodes[i]

        return False