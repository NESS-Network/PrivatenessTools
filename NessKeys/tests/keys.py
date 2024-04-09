import sys    
from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException
from ..keys.Backup import Backup
from ..keys.BlockchainRPC import BlockchainRPC
from ..keys.Faucet import Faucet
from ..keys.Users import Users
from ..keys.Node import Node
from ..keys.Nodes import Nodes
from ..keys.MyNodes import MyNodes
from ..keys.Files import Files
from ..keys.Directories import Directories
from ..keys.Encrypted import Encrypted
from ..keys.Settings import Settings
import json
import random
import uuid

print("==KEYS==")

def rand_int():
    return random.randint(1000, 10000)

def rand_float():
    return random.random()

def rand_chr():
    return chr( ord('a') + random.randint(0, 21) )

def rand_str():
    return  str(uuid.uuid4())

def rand_text(dup: int = 10):
    return  str(uuid.uuid4()) * dup

keydata = {
    "filedata": {
        "vendor": "Privateness",
        "type": "backup",
        "for": "backup"
    },
    "type": 'node',
    "address": 'address',
    "cipher": 'aes',
    "seed": rand_str(),
    "key": rand_text(),
    "files_shadowname": rand_str(),
    "dirs_shadowname": rand_str()
}

keystr = json.dumps(keydata)

backup = Backup()
backup.load(keydata)
keydump = backup.serialize()

print('Backup', keystr == keydump)


keydata = {
    "filedata": {
        "vendor": "Privateness",
        "type": "config",
        "for": "blockchain"
    },
    "rpc-host": rand_str(),
    "rpc-port": rand_int(),
    "rpc-user": rand_str(),
    "rpc-password": rand_str(),
}

keystr = json.dumps(keydata)

key = BlockchainRPC()
key.load(keydata)
keydump = key.serialize()

print('Blockchain RPC', keystr == keydump)


keydata = {
    "filedata": {
        "vendor": "Privateness",
        "type": "key",
        "for": "faucet"
    },
    "keys": {
        "private": rand_str(),
        "verify": rand_str()
    },
    "url": rand_str()
}

key = Faucet()
key.load(keydata)
kd = key.compile()
keydata['worm'] = kd['worm']
keydump = key.serialize()
keystr = json.dumps(keydata)

print('Faucet', keystr == keydump)


keydata = {
    "filedata": {
        "vendor": "Privateness",
        "type": "key",
        "for": "user"
    },
    "current": 'kuser0',
    "users": {
        'kuser0': {
                "username": 'kuser0',
                "private": rand_str(),
                "public": rand_str(),
                "verify": rand_str(),
                "nonce": rand_str(),
                "signatures": {'human': rand_str(), 'company': rand_str()},
                "tags": [rand_str(),rand_str(),rand_str()]
        },
        'kuser1': {
                "username": 'kuser1',
                "private": rand_str(),
                "public": rand_str(),
                "verify": rand_str(),
                "nonce": rand_str(),
                "signatures": {'human': rand_str(), 'company': rand_str()},
                "tags": [rand_str(),rand_str(),rand_str()]
        },
        'kuser2': {
                "username": 'kuser2',
                "private": rand_str(),
                "public": rand_str(),
                "verify": rand_str(),
                "nonce": rand_str(),
                "signatures": {'human': rand_str(), 'company': rand_str()},
                "tags": [rand_str(),rand_str(),rand_str()]
        },
        'kuser3': {
                "username": 'kuser3',
                "private": rand_str(),
                "public": rand_str(),
                "verify": rand_str(),
                "nonce": rand_str(),
                "signatures": {'human': rand_str(), 'company': rand_str()},
                "tags": [rand_str(),rand_str(),rand_str()]
        }
    }
}

key = Users()
key.load(keydata)
kd = key.compile()
keydata['worm'] = kd['worm']
keydump = key.serialize()
keystr = json.dumps(keydata)

print('Users', keystr == keydump)

keydata = {
    "filedata": {
        "vendor": "Privateness",
        "type": "key",
        "for": "node"
    },
    "keys": {
        "private": rand_str(),
        "public": rand_str(),
        "verify": rand_str()
    },
    "url": rand_str(),
    "nonce": rand_str(),
    "master-user": rand_str(),
    "services": [rand_str(),rand_str(),rand_str()],
    "tariff": rand_float(),
}

key = Node()
key.load(keydata)
kd = key.compile()
keydata['worm'] = kd['worm']
keydump = key.serialize()
keystr = json.dumps(keydata)

print('Node', keystr == keydump)

keydata = {
    "filedata": {
        "vendor": "Privateness",
        "type": "data",
        "for": "nodes-list"
    },
    "nodes": [
        {
            "url": rand_str(),
            "public": rand_str(),
            "verify": rand_str(),
            "nonce": rand_str(),
            "master": rand_str(),
            "tariff": rand_int(),
            "tags": [rand_str(),rand_str(),rand_str()]
        },
        {
            "url": rand_str(),
            "public": rand_str(),
            "verify": rand_str(),
            "nonce": rand_str(),
            "master": rand_str(),
            "tariff": rand_int(),
            "tags": [rand_str(),rand_str(),rand_str()]
        },
        {
            "url": rand_str(),
            "public": rand_str(),
            "verify": rand_str(),
            "nonce": rand_str(),
            "master": rand_str(),
            "tariff": rand_int(),
            "tags": [rand_str(),rand_str(),rand_str()]
        },
        {
            "url": rand_str(),
            "public": rand_str(),
            "verify": rand_str(),
            "nonce": rand_str(),
            "master": rand_str(),
            "tariff": rand_int(),
            "tags": [rand_str(),rand_str(),rand_str()]
        }
    ]
}

key = Nodes()
key.load(keydata)
kd = key.compile()
keydump = key.serialize()
keystr = json.dumps(keydata)

print('Nodes', keystr == keydump)

keydata = {
    "filedata": {
        "vendor": "Privateness",
        "type": "service",
        "for": "node"
    },
    "current": ["username", "url1"],
    "nodes": {
        "username": 
            {
                "url1": {
                    "key": rand_str(),
                    "fskey": rand_str(),
                    "cipher": rand_str(),
                    "shadowname": rand_str()
                },
                "url2": {
                    "key": rand_str(),
                    "fskey": rand_str(),
                    "cipher": rand_str(),
                    "shadowname": rand_str()
                },
                "url3": {
                    "key": rand_str(),
                    "fskey": rand_str(),
                    "cipher": rand_str(),
                    "shadowname": rand_str()
                }
            },
    }
}

key = MyNodes()
key.load(keydata)
kd = key.compile()
keydump = key.serialize()
keystr = json.dumps(keydata)

print('My Nodes', keystr == keydump)

keydata = {
    "filedata": {
        "vendor": "Privateness",
        "type": "service",
        "for": "files"
    },
    "files": {
        'xxx': {
            'filename': rand_str(),
            'filepath': rand_str(),
            'size': rand_int(),
            'status': 'n',
            'directory': rand_int()
        },
        'yyy': {
            'filename': rand_str(),
            'filepath': rand_str(),
            'size': rand_int(),
            'status': 'n',
            'directory': rand_int()
        },
        'zzz': {
            'filename': rand_str(),
            'filepath': rand_str(),
            'size': rand_int(),
            'status': 'n',
            'directory': rand_int()
        }
    }
}

key = Files()
key.load(keydata)
kd = key.compile()
keydump = key.serialize()
keystr = json.dumps(keydata)

print('Files', keystr == keydump)

keydata = {
    "filedata": {
        "vendor": "Privateness",
        "type": "encrypted-keys",
        "for": rand_str(),
        "cipher": rand_str()
    },
    "keys": [rand_str(),rand_str(),rand_str()],
    "crc": [rand_str(),rand_str(),rand_str()]
}

key = Encrypted()
key.load(keydata)
kd = key.compile()
keydump = key.serialize()
keystr = json.dumps(keydata)

print('Encrypted', keystr == keydump)

keydata = {
    "filedata": {
        "vendor": "Privateness",
        "type": "settings",
        "for": "settings"
    },
            "entrophy": rand_int(),
            "cipher": rand_str(),
}

key = Settings()
key.load(keydata)
kd = key.compile()
keydump = key.serialize()
keystr = json.dumps(keydata)

print('Settings', keystr == keydump)

