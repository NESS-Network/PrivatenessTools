from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.DeepChecker import DeepChecker
from ..JsonChecker.KeyChecker import KeyChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException
from ..interfaces.NessKey import NessKey
import json
import urllib.parse

class Users(NessKey):

    def load(self, keydata: dict):
        map = {
            "filedata": {
                "vendor": "Privateness",
                "type": "key",
                "for": "user"
            },
            "current": str,
            "users": dict
        }

        JsonChecker.check('User key check', keydata, map)

        map = {
            "username": str,
            "private": str,
            "public": str,
            "verify": str,
            "nonce": str,
            "signatures": dict,
            "tags": list
        }
        
        DeepChecker.check('User key check (users)', keydata, map, 2)

        KeyChecker.check('User key check (current user check)', keydata['users'], keydata["current"], '/users/')

        self.__current = keydata["current"]
        self.__users = keydata["users"]


    def compile(self) -> dict:
        userdata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "key",
                "for": "user"
            },
            "current": self.__current,
            "users": self.__users
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
            "current": self.__current,
            "users": self.__users
        }

        return self.__wrm(userdata)
        
    def nvs(self) -> str:
        return "worm:user:ness:" + self.__current
        
    def print(self):
        return "Privateness User Key <{}>".format(self.__current)

    def getFilename(self):
        return urllib.parse.quote_plus(self.__current) + ".key.json"

    def __wrm(self, user: dict):
        linesep = '\n'
        tab = '\t'
        tab2 = '\t\t'
        tab3 = '\t\t\t'

        sigs = self.__users[self.__current]["signatures"]
        signatures = ""

        for sig in sigs:
            signatures += \
                "{}<signature type=\"{}\">{}</signature>{}".format(tab3, sig, sigs[sig], linesep)

        worm = "<worm>" + linesep + \
            tab + "<user type=\"ness\" " \
               + " public=\"" + self.__users[self.__current]["public"] + "\"" \
               + " verify=\"" + self.__users[self.__current]["verify"] + "\"" \
               + " nonce=\"" + self.__users[self.__current]["nonce"] + "\"" \
               + " tags=\"" + ','.join(self.__users[self.__current]["tags"]) + "\">" + linesep + \
            tab2 + "<signatures> " + linesep + \
            signatures + \
            tab2 + "</signatures>" + linesep + \
            tab2 + "<!-- Here tags may be different for each type of user -->" + linesep + \
            tab + "</user>" + linesep + \
            "</worm>"

        return worm

    def getUsername(self):
        return self.__current

    def getUser(self):
        return self.__users[self.__current]

    def getTags(self):
        return self.__users[self.__current]["tags"]

    def getNonce(self):
        return self.__users[self.__current]["nonce"]

    def getPrivateKey(self):
        return self.__users[self.__current]["private"]

    def getPublicKey(self):
        return self.__users[self.__current]["public"]

    def getVerifyKey(self):
        return self.__users[self.__current]["verify"]

    def getSignatures(self):
        return self.__users[self.__current]["signatures"]