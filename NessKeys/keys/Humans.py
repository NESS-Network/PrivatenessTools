from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.DeepChecker import DeepChecker
from ..JsonChecker.KeyChecker import KeyChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException
from ..interfaces.NessKey import NessKey
import json
import urllib.parse

class Humans(NessKey):

    def __init__(self):
        self.__current = False
        self.__humans = False

    def load(self, keydata: dict):
        map = {
            "filedata": {
                "vendor": "Privateness",
                "type": "key",
                "for": "human"
            },
            "current": str,
            "humans": dict
        }

        JsonChecker.check('Human key check', keydata, map)

        map = {
            "humanname": str,
            "private": str,
            "public": str,
            "verify": str,
            "nonce": str,
            "tags": list
        }
        
        DeepChecker.check('Human key check (humans)', keydata, map, 2)

        KeyChecker.check('Human key check (current human check)', keydata['humans'], keydata["current"], '/humans/')

        self.__current = keydata["current"]
        self.__humans = keydata["humans"]


    def compile(self) -> dict:
        humandata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "key",
                "for": "human"
            },
            "current": self.__current,
            "humans": self.__humans
        }

        # humandata["worm"] = self.__wrm(humandata)

        return humandata

    def worm(self) -> str:
        humandata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "key",
                "for": "human"
            },
            "current": self.__current,
            "humans": self.__humans
        }

        return self.__wrm(humandata)
        
    def nvs(self) -> str:
        return "worm:human:ness:" + self.__current
        
    def print(self):
        return "Privateness Humans Key <{}>".format(self.__current)

    def getFilename(self):
        return "humans.key.json"

    def filename():
        return "humans.key.json"

    def __wrm(self, human: dict):
        linesep = '\n'
        tab = '\t'
        tab2 = '\t\t'
        tab3 = '\t\t\t'

        sigs = self.__humans[self.__current]["signatures"]
        signatures = ""

        for sig in sigs:
            signatures += \
                "{}<signature type=\"{}\">{}</signature>{}".format(tab3, sig, sigs[sig], linesep)

        worm = "<worm>" + linesep + \
            tab + "<human type=\"ness\" " \
               + " public=\"" + self.__humans[self.__current]["public"] + "\"" \
               + " verify=\"" + self.__humans[self.__current]["verify"] + "\"" \
               + " nonce=\"" + self.__humans[self.__current]["nonce"] + "\">"  + linesep + \
            tab2 + "<signatures> " + linesep + \
            signatures + \
            tab2 + "</signatures>" + linesep + \
            tab2 + "<!-- Here tags may be different for each type of human -->" + linesep + \
            tab + "</human>" + linesep + \
            "</worm>"

        return worm

    def getCurrentHuman(self) -> str:
        return self.__current

    def gethumans(self):
        return self.__humans

    def findHuman(self, humanname: str):
        if humanname in self.__humans:
            return self.__humans[humanname]
        else:
            return False

    def getHuman(self):
        return self.__humans[self.__current]

    def setCurrentHuman(self, humanname: str):
        if humanname in self.__humans:
            self.__current = humanname

    def addNewHuman(self, humanname: str, private_key: str, public_key: str, verify_key: str, nonce: str):
        if self.__humans == False:
            self.__humans = {}

        self.__current = humanname

        if not self.__current in self.__humans:
            self.__humans[self.__current] = {}

        self.__humans[self.__current]["humanname"] = humanname
        self.__humans[self.__current]["private"] = private_key
        self.__humans[self.__current]["public"] = public_key
        self.__humans[self.__current]["verify"] = verify_key
        self.__humans[self.__current]["nonce"] = nonce
        # self.__humans[self.__current]["tags"] = tags
        self.__humans[self.__current]["signatures"] = {}

    def getHumanname(self):
        return self.__humans[self.__current]["humanname"]

    def getPrivateKey(self, humanname: str = ''):
        if humanname == '':
            return self.__humans[self.__current]["private"]
        else:
            return self.__humans[humanname]["private"]

    def getPublicKey(self, humanname: str = ''):
        if humanname == '':
            return self.__humans[self.__current]["public"]
        else:
            return self.__humans[humanname]["public"]

    def getVerifyKey(self, humanname: str = ''):
        if humanname == '':
            return self.__humans[self.__current]["verify"]
        else:
            return self.__humans[humanname]["verify"]
        
    def getNonce(self, humanname: str = ''):
        if humanname == '':
            return self.__humans[self.__current]["nonce"]
        else:
            return self.__humans[humanname]["nonce"]

    # def getTags(self):
    #     return self.__humans[self.__current]["tags"]

    def getSignatures(self):
        return self.__humans[self.__current]["signatures"]

    def setPrivateKey(self, private_key: str):
        self.__humans[self.__current]["private"] = private_key

    def setPublicKey(self, public_key: str):
        self.__humans[self.__current]["public"] = public_key

    def setVerifyKey(self, verify_key: str):
        self.__humans[self.__current]["verify"] = verify_key
        
    def setNonce(self, nonce: str,):
        self.__humans[self.__current]["nonce"] = nonce

    # def setTags(self, tags: list):
    #     self.__humans[self.__current]["tags"] = tags

    def addSignature(self, name: str, sig: str):
        self.__humans[self.__current]["signatures"][name] = sig
