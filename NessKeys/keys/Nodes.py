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
            "network": str,
            "public": str,
            "verify": str,
            "nonce": str,
            "master": str,
            "tariff": int,
            "services": list
        }

        DeepChecker.check('Nodes key check (nodes list)', keydata['nodes'], map, 1)

        self.__nodes = keydata["nodes"]


    def compile(self) -> dict:
        keydata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "data",
                "for": "nodes-list"
            },
            "nodes": self.__nodes
        }
        
        return keydata

    def worm(self) -> str:
        return ""
        
    def nvs(self) -> str:
        return ""

    def print(self):
        return "Privateness Nodes storage file"

    def filename():
        return "nodes.key.json"

    def getFilename(self):
        return Nodes.filename()

    def getNodes(self) -> dict:
        return self.__nodes

    def setNodes(self, nodes: list):
        self.__nodes = nodes

    def findNode(self, url: str) -> dict:
        for node in self.__nodes:
            if node['url'] == url:
                return node

        return False