from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.DeepChecker import DeepChecker
from ..JsonChecker.KeyChecker import KeyChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException
from ..interfaces.NessKey import NessKey
import json
import urllib.parse

class Users(NessKey):

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
            # "tags": list
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

        # userdata["worm"] = self.__wrm(userdata)

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
        return "Privateness Users Key <{}>".format(self.__current)

    def getFilename(self):
        return "users.key.json"

    def filename():
        return "users.key.json"

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
               + " nonce=\"" + self.__users[self.__current]["nonce"] + "\">"  + linesep + \
            tab2 + "<signatures> " + linesep + \
            signatures + \
            tab2 + "</signatures>" + linesep + \
            tab2 + "<!-- Here tags may be different for each type of user -->" + linesep + \
            tab + "</user>" + linesep + \
            "</worm>"

        return worm

    def getCurrentUser(self) -> str:
        return self.__current

    def getUsers(self):
        return self.__users

    def findUser(self, username: str):
        if username in self.__users:
            return self.__users[username]
        else:
            return False

    def getUser(self):
        return self.__users[self.__current]

    def setCurrentUser(self, username: str):
        if username in self.__users:
            self.__current = username

    def addNewUser(self, username: str, private_key: str, public_key: str, verify_key: str, nonce: str):
        if self.__users == False:
            self.__users = {}

        self.__current = username

        if not self.__current in self.__users:
            self.__users[self.__current] = {}

        self.__users[self.__current]["username"] = username
        self.__users[self.__current]["private"] = private_key
        self.__users[self.__current]["public"] = public_key
        self.__users[self.__current]["verify"] = verify_key
        self.__users[self.__current]["nonce"] = nonce
        # self.__users[self.__current]["tags"] = tags
        self.__users[self.__current]["signatures"] = {}

    def getUsername(self):
        return self.__users[self.__current]["username"]

    def getPrivateKey(self, username: str = ''):
        if username == '':
            return self.__users[self.__current]["private"]
        else:
            return self.__users[username]["private"]

    def getPublicKey(self, username: str = ''):
        if username == '':
            return self.__users[self.__current]["public"]
        else:
            return self.__users[username]["public"]

    def getVerifyKey(self, username: str = ''):
        if username == '':
            return self.__users[self.__current]["verify"]
        else:
            return self.__users[username]["verify"]
        
    def getNonce(self, username: str = ''):
        if username == '':
            return self.__users[self.__current]["nonce"]
        else:
            return self.__users[username]["nonce"]

    # def getTags(self):
    #     return self.__users[self.__current]["tags"]

    def getSignatures(self):
        return self.__users[self.__current]["signatures"]

    def setPrivateKey(self, private_key: str):
        self.__users[self.__current]["private"] = private_key

    def setPublicKey(self, public_key: str):
        self.__users[self.__current]["public"] = public_key

    def setVerifyKey(self, verify_key: str):
        self.__users[self.__current]["verify"] = verify_key
        
    def setNonce(self, nonce: str,):
        self.__users[self.__current]["nonce"] = nonce

    # def setTags(self, tags: list):
    #     self.__users[self.__current]["tags"] = tags

    def addSignature(self, name: str, sig: str):
        self.__users[self.__current]["signatures"][name] = sig
