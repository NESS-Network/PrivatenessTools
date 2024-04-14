from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException
from ..interfaces.NessKey import NessKey
import urllib.parse

class Node(NessKey):

    def load(self, keydata: dict):
        map = {
            "filedata": {
                "vendor": "Privateness",
                "type": "key",
                "for": "node"
            },
            "keys": {
                "private": str,
                "public": str,
                "verify": str
            },
            "url": str,
            "network": str,
            "nonce": str,
            "master-user": str,
            "services": list,
            "tariff": int,
        }

        JsonChecker.check('Node key check', keydata, map)

        self.__private_key = keydata["keys"]["private"]
        self.__public_key = keydata["keys"]["public"]
        self.__verify_key = keydata["keys"]["verify"]
        self.__url = keydata["url"]
        self.__nonce = keydata["nonce"]
        
        if "network" in keydata:
            self.__network = keydata["network"]
        else:
            self.__network = "inet"

        self.__master_user = keydata["master-user"]
        self.__services = keydata["services"]
        self.__tariff = keydata["tariff"]

    def compile(self) -> dict:
        nodedata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "key",
                "for": "node"
            },
            "keys": {
                "private": self.__private_key,
                "public": self.__public_key,
                "verify": self.__verify_key
            },
            "url": self.__url,
            "network": self.__network,
            "nonce": self.__nonce,
            "master-user": self.__master_user,
            "services": self.__services,
            "tariff": self.__tariff,
        }

        nodedata["worm"] = self.__wrm(nodedata)

        return nodedata

    def worm(self) -> str:
        nodedata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "key",
                "for": "node"
            },
            "keys": {
                "private": self.__private_key,
                "public": self.__public_key,
                "verify": self.__verify_key
            },
            "url": self.__url,
            "nonce": self.__nonce,
            "network": self.__network,
            "master-user": self.__master_user,
            "services": self.__services,
            "tariff": self.__tariff,
        }

        return self.__wrm(nodedata)
        
    def nvs(self) -> str:
        return "worm:node:ness:" + self.__url
        
    def print(self):
        return "Privateness Node Key: <{}>\nNetwork: <{}>\nMaster User:<{}>\nTariff:<{}>".format(self.__url, self.__network, self.__master_user, self.__tariff)

    def getFilename(self):
        return urllib.parse.quote_plus(self.__url) + ".key.json"

    def __wrm(self, nodedata: dict):
        linesep = '\n'
        tab = '\t'
        tab2 = '\t\t'

        worm = "<worm>"+linesep+\
            tab + "<node type=\"ness\" url=\"" + nodedata["url"] + "\" network=\"" + nodedata["network"] + "\" nonce=\"" + nodedata["nonce"] + "\"   " + \
            " verify=\"" + nodedata['keys']["verify"] + "\" public=\"" + nodedata['keys']["public"] + "\" master-user=\"" + \
            nodedata["master-user"] + "\" tariff=\"" + str(nodedata["tariff"]) + "\" services=\"" + ','.join(nodedata["services"]) + "\">" + linesep + \
            tab2 + "<!-- Here tags may be different for each type of node or each node -->" + linesep + \
            tab + "</node>" + linesep + \
            "</worm>"

        return worm

    def getServices(self):
        return self.__services

    def getNonce(self):
        return self.__nonce

    def getNetwork(self):
        return self.__network

    def getPrivateKey(self):
        return self.__private_key

    def getPublicKey(self):
        return self.__public_key

    def getVerifyKey(self):
        return self.__verify_key

    def getUrl(self):
        return self.__url

    def getTariff(self):
        return self.__tariff

    def getMasterUser(self):
        return self.__master_user

    def setServices(self, services: str):
        self.__services = services.split(',')

    def setNetwork(self, network: str):
        self.__network = network

    def setNonce(self, nonce: str):
        self.__nonce = nonce

    def setPrivateKey(self, private_key: str):
        self.__private_key = private_key

    def setPublicKey(self, public_key: str):
        self.__public_key = public_key

    def setVerifyKey(self, verify_key: str):
        self.__verify_key = verify_key

    def setUrl(self, url: str):
        self.__url = url

    def setNonve(self, nonce: str):
        self.__nonce = nonce

    def setTariff(self, tariff: str):
        self.__tariff = tariff

    def setMasterUser(self, master_user: str):
        self.__master_user = master_user