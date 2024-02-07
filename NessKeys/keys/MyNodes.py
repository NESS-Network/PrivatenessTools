from NessKeys.interfaces.NessKey import NessKey
from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.DeepChecker import DeepChecker
from ..JsonChecker.KeyChecker import KeyChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException

class MyNodes(NessKey):

    def load(self, keydata: dict):
        map = {
            "filedata": {
                "vendor": "Privateness",
                "type": "service",
                "for": "node"
            },
            "nodes": dict,
            "current": list,
        }

        JsonChecker.check('MyNodes', keydata, map)

        map = {
            "key": str,
            "fskey": str,
            "cipher": str,
            "shadowname": str
        }

        DeepChecker.check('MyNodes key check (nodes list)', keydata['nodes'], map, 2)

        KeyChecker.check('MyNodes key check (current user)', keydata['nodes'], keydata['current'][0], '/nodes/')

        KeyChecker.check('MyNodes key check (current node)', keydata['nodes'][keydata['current'][0]], keydata['current'][1], '/nodes/' + keydata['current'][0] + '/')

        self.__current = keydata["current"]
        self.__nodes = keydata["nodes"]

    def compile(self) -> dict:
        appdata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "service",
                "for": "node"
            },
            "current": self.__current,
            "nodes": self.__nodes
        }

        return appdata

    def worm(self) -> str:
        return ""
        
    def nvs(self) -> str:
        return ""

    def print(self):
        return "Privateness User Nodes"

    def filename():
        return "my-nodes.json"

    def getFilename(self):
        return MyNodes.filename()

    def getCurrentNode(self) -> list:
        return self.__current

    def getCurrentNodeUsername(self) -> list:
        return self.__current[0]

    def getCurrentNodeUrl(self) -> list:
        return self.__current[1]

    def findNode(self, user_name: str, node_url: str):
        if user_name in self.__nodes and node_url in self.__nodes[user_name]:
            return self.__nodes[user_name][node_url]
        else:
            return False

    def changeCurrentNode(self, user_name: str, node_url: str) -> bool:
        if user_name in self.__nodes and node_url in self.__nodes[user_name]:
            self.__current = [user_name, node_url]
            return True
        else:
            return False

    def addNode(self, user_name: str, node_url: str, user_shadowname: str, key: str, cipher: str):
        self.__nodes[user_name][node_url] = \
            {'shadowname': user_shadowname, 'key': key, 'cipher': cipher}

    def updateNode(self, user_name: str, node_url: str, user_shadowname: str, key: str, cipher: str):
        self.__nodes[user_name][node_url] \
            .update({'shadowname': user_shadowname, 'key': key, 'cipher': cipher})

    def removeNode(self, user_name: str, node_url: str):
        del self.__nodes[user_name][node_url]
