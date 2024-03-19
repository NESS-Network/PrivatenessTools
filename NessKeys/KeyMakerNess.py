from NessKeys.interfaces.NessKey import NessKey
from NessKeys.interfaces.KeyMaker import KeyMaker


from NessKeys.keys.Backup import Backup
from NessKeys.keys.BlockchainRPC import BlockchainRPC
from NessKeys.keys.Faucet import Faucet
from NessKeys.keys.Users import Users
from NessKeys.keys.Node import Node
from NessKeys.keys.Nodes import Nodes
from NessKeys.keys.MyNodes import MyNodes
from NessKeys.keys.Files import Files
from NessKeys.keys.Directories import Directories
from NessKeys.keys.Encrypted import Encrypted

class KeyMakerNess(KeyMaker):
    def make(self, keydata: dict) -> NessKey:

        filedata = keydata['filedata']

        vendor = filedata['vendor']
        _type = filedata['type']
        _for = filedata['for']

        if vendor == "Privateness" and _type == 'backup' and _for == 'backup':
            key = Backup()
            key.load(keydata)
            return key

        elif vendor == "Privateness" and _type == 'config' and _for == 'blockchain':
            key = BlockchainRPC()
            key.load(keydata)
            return key

        elif vendor == "Privateness" and _type == 'key' and _for == 'faucet':
            key = Faucet()
            key.load(keydata)
            return key

        elif vendor == "Privateness" and _type == 'key' and _for == 'user':
            key = Users()
            key.load(keydata)
            return key

        elif vendor == "Privateness" and _type == 'key' and _for == 'node':
            key = Node()
            key.load(keydata)
            return key

        elif vendor == "Privateness" and _type == 'data' and _for == 'nodes-list':
            key = Nodes()
            key.load(keydata)
            return key

        elif vendor == "Privateness" and _type == 'service' and _for == 'node':
            key = MyNodes()
            key.load(keydata)
            return key

        elif vendor == "Privateness" and _type == 'service' and _for == 'files':
            key = Files()
            key.load(keydata)
            return key

        elif vendor == "Privateness" and _type == 'service' and _for == 'files-directories':
            key = Directories()
            key.load(keydata)
            return key

        elif vendor == "Privateness" and _type == 'encrypted-keys':
            key = Encrypted()
            key.load(keydata)
            return key

        return False