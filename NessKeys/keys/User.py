from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.DeepChecker import DeepChecker
from ..JsonChecker.KeyChecker import KeyChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException
from ..interfaces.NessKey import NessKey
import json
import urllib.parse

class User(NessKey):

    def __init__(self):
        self.__current = False
        self.__users = False

    def load(self, keydata: dict):
        map = {
            "filedata": {
                "vendor": "Privateness",
                "type": "key",
                "for": "user"
            },
            "username": str,
            "private": str,
            "public": str,
            "verify": str,
            "nonce": str,
            "signatures": dict,
        }

        JsonChecker.check('User key check', keydata, map)

        self.__username = keydata["username"]
        self.__private = keydata["private"]
        self.__public = keydata["public"]
        self.__verify = keydata["verify"]
        self.__nonce = keydata["nonce"]
        self.__signatures = keydata["signatures"]


    def compile(self) -> dict:
        userdata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "key",
                "for": "user"
            },
            "username": self.__username,
            "private": self.__private,
            "public": self.__public,
            "verify": self.__verify,
            "nonce": self.__nonce,
            "signatures": self.__signatures
        }

        userdata["worm"] = self.__wrm(userdata)

        return userdata

    def worm(self) -> str:
        userdata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "key",
                "for": "user"
            },
            "username": self.__username,
            "private": self.__private,
            "public": self.__public,
            "verify": self.__verify,
            "nonce": self.__nonce,
            "signatures": self.__signatures
        }

        return self.__wrm(userdata)
        
    def nvs(self) -> str:
        return "worm:user:ness:" + self.__username
        
    def print(self):
        return "Privateness User Key <{}>".format(self.__username)

    def getFilename(self):
        return "user.key.json"

    def filename():
        return "user.key.json"

    def __wrm(self, user: dict):
        linesep = '\n'
        tab = '\t'
        tab2 = '\t\t'
        tab3 = '\t\t\t'

        sigs = self.__signatures
        signatures = ""

        for sig in sigs:
            signatures += \
                "{}<signature type=\"{}\">{}</signature>{}".format(tab3, sig, sigs[sig], linesep)

        worm = "<worm>" + linesep + \
            tab + "<user type=\"ness\" " \
               + " public=\"" + self.__public + "\"" \
               + " verify=\"" + self.__verify + "\"" \
               + " nonce=\"" + self.__nonce + "\">"  + linesep + \
            tab2 + "<signatures> " + linesep + \
            signatures + \
            tab2 + "</signatures>" + linesep + \
            tab2 + "<!-- Here tags may be different for each type of user -->" + linesep + \
            tab + "</user>" + linesep + \
            "</worm>"

        return worm

    def getUsername(self):
        return self.__username

    def getPrivateKey(self):
        return self.__private

    def getPublicKey(self):
        return self.__public

    def getVerifyKey(self):
        return self.__verify
        
    def getNonce(self):
        return self.__nonce

    def getSignatures(self):
        return self.__signatures

    def setPrivateKey(self, private_key: str):
        self.__private = private_key

    def setPublicKey(self, public_key: str):
        self.__public = public_key

    def setVerifyKey(self, verify_key: str):
        self.__verify = verify_key
        
    def setNonce(self, nonce: str,):
        self.__nonce = nonce

    def addSignature(self, name: str, sig: str):
        self.__signatures[name] = sig
