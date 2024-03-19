from framework.Container import Container

from NessKeys.KeyManager import KeyManager
from NessKeys.StorageJson import StorageJson
from NessKeys.KeyMakerNess import KeyMakerNess
from NessKeys.keys.MyNodes import MyNodes
from NessKeys.keys.Nodes import Nodes
from NessKeys.keys.Users import Users
from NessKeys.CryptorMaker import CryptorMaker
from NessKeys.BlockCryptor import BlockCryptor
from NessKeys.ConsoleOutput import ConsoleOutput

from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.MyNodesFileDoesNotExist import MyNodesFileDoesNotExist
from NessKeys.exceptions.NodeError import NodeError
from NessKeys.exceptions.AuthError import AuthError
from NessKeys.exceptions.UserNotFound import UserNotFound

from services.node import node
from services.files import files

import json
from ness.NessAuth import NessAuth
import math
import os
import requests
from Crypto.Random import get_random_bytes
from base64 import b64encode
from base64 import b64decode

from framework.ARGS import ARGS

class ESTester:

    data_user = {}
    data_node = {}

    def __init__(self):
        storage = StorageJson()
        maker = KeyMakerNess()

        self.km = KeyManager(storage, maker)

        self.Users = self.km.getUsersKey()
        self.Nodes = self.km.getNodesKey()

        self.ness_auth = NessAuth()

    def test(self, username: str, node_url: str):
        km = Container.KeyManager()

        km.initFilesAndDirectories()

        fm = Container.FileManager()
        
        # Init
        fm.join(username, node_url)

        # Encrypt

        # Upload

        # Download

        # Decrypt

        # Compare

        return True


print('==Test encrypted storage==')

if ARGS.args(['auth', str, str]):
    tester = ESTester()

    try:
        tester.test(ARGS.arg(2), ARGS.arg(3))
    except UserNotFound as e:
        print("User '{}' is not in users list".format(e.username))
    except NodeNotFound as e:
        print("NODE '{}' is not in nodes list".format(e.node))