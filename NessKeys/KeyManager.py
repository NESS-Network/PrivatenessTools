import os
import glob
import random
import sys
import glob
from pathlib import Path
from base64 import b64encode
from base64 import b64decode
import json
import urllib.parse
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from nacl.signing import SigningKey, VerifyKey
from nacl.public import PrivateKey, PublicKey
from nacl.encoding import Base64Encoder
import validators
import lxml.etree as etree
from random_word import RandomWords

import NessKeys.interfaces.NessKey as NessKey
from NessKeys.keys.Files import Files as FilesKey
from NessKeys.keys.Directories import Directories as DirectoriesKey
from NessKeys.keys.Users import Users as Users
from NessKeys.keys.Node import Node as NodeKey
# from NessKeys.keys.UserLocal import UserLocal
from NessKeys.keys.Encrypted import Encrypted
from NessKeys.keys.BlockchainRPC import BlockchainRPC as BlockchainRpcKey
from NessKeys.keys.Nodes import Nodes
from NessKeys.keys.MyNodes import MyNodes
from NessKeys.keys.Faucet import Faucet as Faucetkey
from NessKeys.keys.Backup import Backup as BackupKey
from NessKeys.keys.Settings import Settings as SettingsKey
import NessKeys.interfaces.KeyMaker as KeyMaker
import NessKeys.interfaces.Storage as Storage
import NessKeys.interfaces.NessKey as NessKey
import NessKeys.interfaces.Cryptor as Cryptor
import uuid
import NessKeys.Prng as prng
from NessKeys.CryptorMaker import CryptorMaker
from NessKeys.PasswordCryptor import PasswordCryptor
from NessKeys.TextCryptor import TextCryptor


from NessKeys.exceptions.BlockchainSettingsFileNotExist import BlockchainSettingsFileNotExist
from NessKeys.exceptions.NodesFileDoesNotExist import NodesFileDoesNotExist
from NessKeys.exceptions.EmptyNodesList import EmptyNodesList
from NessKeys.exceptions.NodeError import NodeError
from NessKeys.exceptions.NodeNotInList import NodeNotInList
from NessKeys.exceptions.UserNotFound import UserNotFound
from NessKeys.exceptions.UsersKeyDoesNotExist import UsersKeyDoesNotExist
from NessKeys.exceptions.FilesKeyDoesNotExist import FilesKeyDoesNotExist
from NessKeys.exceptions.DirectoriesKeyDoesNotExist import DirectoriesKeyDoesNotExist
from NessKeys.exceptions.MyNodesFileDoesNotExist import MyNodesFileDoesNotExist
from NessKeys.JsonChecker.exceptions.LeafBuildException import LeafBuildException

class KeyManager:

    def __init__(self, storage: Storage, key_maker: KeyMaker):
        self.__storage = storage
        self.__key_maker = key_maker
        self.directory = str(Path.home()) + "/.privateness-keys"
        self.keys = glob.glob(self.directory + '/*.json')

    def getLocalKeyFiles(self):
        return self.keys

    def fileName(self, filename: str) -> str:
        return self.directory + "/" + filename

    def fileExists(self, filename: str) -> bool:
        return os.path.exists(self.fileName(filename))

    def saveKey(self, key: NessKey):
        self.__storage.save(key.compile(), self.fileName(key.getFilename()))

    def keyExists(self, key: NessKey):
        return os.path.exists(self.fileName(key.getFilename()))

    def initKey(self, key: NessKey):
        if not self.keyExists(key):
            self.saveKey(key)

    def loadKey(self, key: NessKey):
        if self.keyExists(key):
            filename = self.fileName(key.getFilename())
            keydata = self.__storage.restore(filename)
            key.load(keydata)

        return key

    def createUsersKey(self, username: str, tags: str, entropy: int):
        userkey = Users()
        filename = self.fileName(userkey.getFilename())

        keydata = self.__storage.restore(filename)

        if keydata != False:
            userkey.load(keydata)

        key_pair = self.__keypair(entropy)

        nonce = b64encode(get_random_bytes(16)).decode('utf-8')
        tags = tags.split(',')

        userkey.addNewUser(username, key_pair[0], key_pair[2], key_pair[1], nonce, tags)

        self.__storage.save(userkey.compile(), filename)

    def changeCurrentUser(self, username: str):
        userkey = Users()
        filename = self.fileName(userkey.getFilename())

        keydata = self.__storage.restore(filename)

        if keydata != False:
            userkey.load(keydata)

        if userkey.findUser(username) == False:
            raise UserNotFound(username)

        userkey.setCurrentUser(username)

        self.__storage.save(userkey.compile(), filename)

    def showUsersKey(self) -> dict|bool:
        userkey = Users()
        filename = self.fileName(userkey.getFilename())

        keydata = self.__storage.restore(filename)

        if keydata == False:
            return False

        userkey.load(keydata)

        return {
            'current': userkey.getCurrentUser(),
            'users': userkey.getUsers(),
            'nvs': userkey.nvs(),
            'worm': userkey.worm()
        }

    def getCurrentUser(self) -> str|bool:
        userkey = Users()
        filename = self.fileName(userkey.getFilename())

        keydata = self.__storage.restore(filename)

        if keydata == False:
            return False

        userkey.load(keydata)

        return userkey.getCurrentUser()


    def createNodeKey(self, url: str, tariff: int, masterUser: str, tags: str, entropy: int):
        keypair = self.__keypair(entropy)
        filename = urllib.parse.quote_plus(url) + ".key.json"

        nodekey = NodeKey()
        nodekey.setUrl(url)
        nodekey.setTariff(tariff)
        nodekey.setMasterUser(masterUser)
        nodekey.setTags(tags)
        nodekey.setPrivateKey(keypair[0])
        nodekey.setVerifyKey(keypair[1])
        nodekey.setPublicKey(keypair[2])
        nodekey.setNonce(b64encode(get_random_bytes(16)).decode('utf-8'))

        self.__storage.save(nodekey.compile(), filename)

    def createFaucetkey(self, url: str, entropy: int):
        keypair = self.__keypair(entropy)

        fkey = Faucetkey()
        fkey.setPrivateKey(keypair[0])
        fkey.setVerifyKey(keypair[1])
        fkey.setUrl(url)

        self.__storage.save(fkey.compile(), fkey.getFilename())

    def createBackupKey(self, backup_type: str, address: str, entropy: int) -> BackupKey:
        w = self.__generate_word_seed(entropy)
        seed = ' '.join(w)
        key = self.KeyFromSeed(seed)

        bkey = BackupKey()
        bkey.setType(backup_type)
        bkey.setAddress(address)
        bkey.setSeed(seed)
        bkey.setKey(key)
        
        self.__storage.save(bkey.compile(), self.fileName(bkey.getFilename()))

        return bkey

    def getBackupKey(self) -> BackupKey:
        bkey = BackupKey()
        filename = self.fileName(bkey.getFilename())

        if not os.path.exists(filename):
            return False

        keydata = self.__storage.restore(filename)
        bkey.load(keydata)

        return bkey

    def __getKey(self, filename: str) -> NessKey:
        keydata = self.__storage.restore(filename)
        return self.__key_maker.make(keydata)

    def showKey(self, filename: str):
        Key = self.__getKey(filename)

        if Key:
            return Key.print()

    def showKeyFull(self, filename: str):
        Key = self.__getKey(filename)

        if Key:
            return Key.build()

    def showKeyNVS(self, filename: str):
        Key = self.__getKey(filename)

        if Key:
            return Key.nvs()

    def showKeyWorm(self, filename: str):
        Key = self.__getKey(filename)

        if Key:
            return Key.worm()

    # def changeUserKeypair(self, filename: str, keypairIndex: int):
    #     userdata = self.__storage.restore(filename)
    #     userkey = Users(userdata)
    #     userkey.changeKeypair(keypairIndex)
    #     self.__storage.save(userkey.compile(), filename)

    def listKeys(self, filename: str, password: str = 'qwerty123'):
        cryptor = CryptorMaker.make('salsa20')
        pc = PasswordCryptor(cryptor, password)

        Key = self.__getKey(filename)
        packedKeys = Key.getKeys()
        crc = Key.getCrc()

        i = 0
        for packedKey in packedKeys:
            # Unpack key
            original_key = pc.decrypt( b64decode(packedKey), b64decode(crc[i]) ).decode('utf-8')
            # Restore key
            keydata = json.loads(original_key)
            key = self.__key_maker.make(keydata)
            # Print Key
            i += 1
            print(" # " + str(i))
            print(key.print())

        return True

    def unpackKeysPassword(self, filename: str, password: str = 'qwerty123', dir = ""):
        cryptor = CryptorMaker.make('salsa20')
        pc = PasswordCryptor(cryptor, password)

        Key = self.__getKey(filename)
        packedKeys = Key.getKeys()
        crc = Key.getCrc()

        i = 0
        for packedKey in packedKeys:
            # Unpack key
            original_key = pc.decrypt( b64decode(packedKey), b64decode(crc[i]) ).decode('utf-8')
            # Restore key
            keydata = json.loads(original_key)
            key = self.__key_maker.make(keydata)
            # Save Key
            self.__storage.save(key.compile(), dir + key.getFilename())
            i += 1

        return True

    def packKeysPassword(self, keysFiles: list, outFilename: str, password: str = 'qwerty123'):
        cryptor = CryptorMaker.make('salsa20')
        pc = PasswordCryptor(cryptor, password)
        keys = []
        crc = []

        for keysFile in keysFiles:
            # Load key
            Key = self.__getKey(keysFile)
            skey = Key.serialize()
            # CRC
            crc.append( b64encode(pc.crc(bytes(skey, 'utf8'))).decode('utf-8') )
            # Pack key
            skey = b64encode(pc.encrypt(bytes(skey, 'utf8'))).decode('utf-8')
            keys.append(skey)

        keydata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "encrypted-keys",
                "for": "",
                "cipher": cryptor.getCipher()
            },
            "keys": keys,
            "crc": crc
        }

        encrypted = Encrypted(keydata)
        
        self.__storage.save(encrypted.compile(), outFilename)



    def unpackKeys(self, key: bytes, filename: str):
        Key = self.__getKey(filename)
        packedKeys = Key.getKeys()
        crc = Key.getCrc()
        cipher = Key.getCipher()

        cryptor = CryptorMaker.make(cipher)
        pc = TextCryptor(cryptor, key)

        try:
            i = 0
            for packedKey in packedKeys:
                # Unpack key
                original_key = pc.decrypt( b64decode(packedKey), b64decode(crc[i]) ).decode('utf-8')
                # Restore key
                keydata = json.loads(original_key)
                key = self.__key_maker.make(keydata)
                # Save Key
                self.__storage.save(key.compile(), self.fileName(key.getFilename()))
                i += 1
        except ValueError as error:
            print(' !!! Decryption of {} failed: {}'.format(filename, error))
            return False

        return True

    def packKeys(self, keysFiles: list, cipher: str, key: bytes, outFilename: str):
        cryptor = CryptorMaker.make(cipher)
        pc = TextCryptor(cryptor, key)
        keys = []
        crc = []

        for keysFile in keysFiles:
            # Load key
            try:
                Key = self.__getKey(keysFile)
                err_msg = "Wrong format"
            except LeafBuildException as error:
                Key = False
                err_msg = error.msg
            
            if Key != False:
                skey = Key.serialize()
                # CRC
                crc.append('')
                # Pack key
                skey = b64encode(pc.encrypt(bytes(skey, 'utf8'))).decode('utf-8')
                keys.append(skey)

                print(keysFile, 'OK')

            else:
                print(keysFile, 'Failed ({})'.format(err_msg))

        encrypted = Encrypted()
        encrypted.setFor("Backup")
        encrypted.setKeys(keys)
        encrypted.setCrc(crc)
        encrypted.setCipher(cipher)
        
        self.__storage.save(encrypted.compile(), outFilename)

    def hasUsersKey(self) -> bool:
        return self.fileExists(Users.filename())

    def getUsersKey(self):
        filename = self.fileName(Users.filename())

        if os.path.exists(filename):
            ukey = Users()
            keydata = self.__storage.restore(filename)
            ukey.load(keydata)
            return ukey
        else:
            raise UsersKeyDoesNotExist()


    # def init(self, user_keyfile: str):
    #     userdata = self.__storage.restore(user_keyfile)
    #     userkey = Users(userdata)

    #     userdata = {
    #         "filedata": {
    #             "vendor": "Privateness",
    #             "type": "key",
    #             "for": "user-local"
    #         },
    #         "username": userkey.getUsername(),
    #         "nonce": userkey.getNonce(),
    #         "keys": {
    #             "private": userkey.getPrivateKey(),
    #             "public": userkey.getPublicKey(),
    #             "verify": userkey.getVerifyKey(),
    #         },
    #     }

    #     localkey = UserLocal(userdata)

    #     if not os.path.exists(self.directory):
    #         os.mkdir(self.directory)

    #     self.__storage.save(localkey.compile(), self.fileName(UserLocal.filename()))


    # def init_node(self, node_keyfile: str):
    #     keydata = self.__storage.restore(node_keyfile)
    #     nodekey = NodeKey(keydata)

    #     node_data = {
    #         "master-user": nodekey.getMasterUser(),
    #         "nonce": nodekey.getNonce(),
    #         "private": nodekey.getPrivateKey(),
    #         "public": nodekey.getPublicKey(),
    #         "tariff": nodekey.getTariff(),
    #         "period": "7200",
    #         "delta": "1200",
    #         "url": nodekey.getUrl(),
    #         "verify": nodekey.getVerifyKey(),
    #         "slots": 10
    #     }

    #     self.__storage.save(node_data, 'node.json')

    def save(self, outFilename: str, password: str = 'qwerty123'):
        keysFiles = glob.glob(self.directory + "/*.json" )

        keysFilesWithDir = []
        for keyFile in keysFiles:
            keysFilesWithDir.append(keyFile)
        
        return self.packKeys(keysFilesWithDir, outFilename, password)

    def restore(self, inFilename: str, password: str = 'qwerty123'):
        return self.unpackKeys(inFilename, password, self.directory + '/')


    def hasBlockchainSettings(self) -> dict:
        return self.fileExists(BlockchainRPC.filename())


    def hasNodesList(self) -> bool:
        return self.fileExists(Nodes.filename())

    def getNodesKey(self):
        nodedata = self.__storage.restore(self.fileName(Nodes.filename()))
        nodes = Nodes()
        nodes.load(nodedata)
        return nodes

    def getNodesList(self) -> list:
        nodedata = self.__storage.restore(self.fileName(Nodes.filename()))
        nodes = Nodes()
        nodes.load(nodedata)
        return nodes.compile()['nodes']

    def saveNodesList(self, nodes_list: list):
        nodes = Nodes()

        if self.fileExists(Nodes.filename()):
            nodedata = self.__storage.restore(self.fileName(Nodes.filename()))
            nodes.load(nodedata)

        nodes.setNodes(nodes_list)
        self.__storage.save(nodes.compile(), self.fileName(Nodes.filename()))

    def saveBlockchainSettings(self, host: str, port: int, user: str, password: str):
        key = BlockchainRpcKey()

        key.setHost(host)
        key.setPort(port)
        key.setUser(user)
        key.setPassword(password)

        self.__storage.save(key.compile(), self.fileName(BlockchainRpcKey.filename()))

    def getBlockchainSettings(self) -> dict:
        filename = self.fileName(BlockchainRpcKey.filename())

        if not os.path.exists(filename):
            raise BlockchainSettingsFileNotExist()

        key = BlockchainRpcKey()
        keydata = self.__storage.restore(filename)
        key.load(keydata)

        return {'host': key.getHost(), 'port': key.getPort(), 'user': key.getUser(), 'password': key.getPassword()}

    def listNodes(self) -> dict:
        filename = self.fileName(Nodes.filename())

        if not os.path.exists(filename):
            raise NodesFileDoesNotExist()

        keydata = self.__storage.restore(filename)
        key = Nodes()
        key.load(keydata)
        return key.getNodes()


    def getRandomNode(self) -> dict:
        nodes = self.listNodes()

        if (len(nodes) == 0):
            raise EmptyNodesList()

        rnd = random.randrange(0, len(nodes))
        cnt = 0
            
        for node in nodes:
            if cnt == rnd:
                return node
            cnt += 1

    def hasMyNodes(self) -> bool:
        return os.path.exists( self.fileName(MyNodes.filename()) )

    def initMyNodes(self):
        key = MyNodes()
        self.initKey(key)

    def getMyNodesKey(self):
        mkey =  MyNodes()
        self.loadKey(mkey)
        return mkey


    def isNodeInMyNodes(self, node_name: str) -> bool:
        key = self.getMyNodesKey()

        return (key.findNode(node_name) != False)

    def isNodeInNodesList(self, node_name: str) -> bool:
        key = Nodes()
        
        if not self.keyExists(key):
            raise NodesFileDoesNotExist()

        self.loadKey(key)

        return (key.findNode(node_name) != False)

    def getCurrentNodeName(self):
        if self.hasMyNodes():
            key = self.getMyNodesKey()
            current_node = key.getCurrentNode()

            if len(current_node) == 0:
                return False
            else:
                return current_node[1]
        else:
            return False

    def getCurrentNode(self) -> dict:
        nodes = self.listNodes()

        return nodes[self.getCurrentNodeName()]

    def hasNode(self, node_name: str):
        nkey = self.getMyNodesKey()
        ukey = self.getUsersKey()
        username = ukey.getUsername()

        return nkey.findNode(username, node_name)

    def saveCurrentNode(self, node_name: str, user_shadowname: str, key: str, fskey: str, cipher: str):
        nkey = self.getMyNodesKey()
        ukey = self.getUsersKey()
        username = ukey.getUsername()

        if not nkey.findNode(username, node_name):
            nkey.addNode(username, node_name, user_shadowname, key, fskey, cipher)
        else:
            nkey.updateNode(username, node_name, user_shadowname, key, fskey, cipher)

        self.saveKey(nkey)


    def changeCurrentNode(self, node_name: str):
        nkey = self.getMyNodesKey()
        ukey = self.getUsersKey()
        username = ukey.getUsername()

        if not nkey.findNode(username, node_name):
            raise NodeNotInList()

        nkey.changeCurrentNode(username, node_name)

        self.saveKey(nkey)

    def hasFilesKey(self) -> bool:
        return self.hasFiles()

    def hasDirectoriesKey(self) -> bool:
        key = DirectoriesKey()
        return self.keyExists(key)

    def initFiles(self):
        key = FilesKey()
        self.initKey(key)

    def initDirectories(self):
        key = DirectoriesKey()
        self.initKey(key)

    def initFilesAndDirectories(self):
        self.initDirectories()
        self.initFiles()

        node_name = self.getCurrentNodeName()
        username = self.getCurrentUser()

        if node_name != False:
            dk = self.getDirectoriesKey()
            dk.initDirectories(username, node_name)

            fk = self.getFilesKey()
            fk.initFiles(username, node_name)

            self.saveKey(dk)
            self.saveKey(fk)

    def getFilesKey(self) -> FilesKey:
        fk = FilesKey()
        self.loadKey(fk)
        return fk

    def getDirectoriesKey(self) -> DirectoriesKey:
        dk = DirectoriesKey()
        self.loadKey(dk)
        return dk

    def initKeys(self):
        self.initSettings()
        self.initMyNodes()
        self.initFilesAndDirectories()

    def isFile(self, ID: str) -> bool:
        return not ID.isnumeric()

    def findFile(self, filename: str):
        return self.getFilesKey().getFileByFilename(self.getCurrentUser(), self.getCurrentNodeName(), filename)
    
    def findEncUplFile(self, filename: str):
        return self.getFilesKey().getEncUplFileByFilename(self.getCurrentUser(), self.getCurrentNodeName(), filename)
    
    def getFile(self, shadowname: str):
        return self.getFilesKey().getFile(self.getCurrentUser(), self.getCurrentNodeName(), shadowname)
    
    def getDirectory(self, ID: int):
        return self.getDirectoriesKey().get(self.getCurrentUser(), self.getCurrentNodeName(), ID)
    
    def tree(self):
        return self.getDirectoriesKey().tree(self.getCurrentUser(), self.getCurrentNodeName())

    def getDirectoryParentID(self, ID: int):
        return self.getDirectoriesKey().get_parent_id(self.getCurrentUser(), self.getCurrentNodeName(), ID)

    def mkdir(self, parent_id: int, name: str) -> int:
        dk = self.getDirectoriesKey()
        id = dk.mkdir(self.getCurrentUser(), self.getCurrentNodeName(), parent_id, name)
        # print(dk.compile(), self.fileName(dk.getFilename()))
        # self.__storage.save(dk.compile(), self.fileName(dk.getFilename()) )
        self.saveKey(dk)
        return id

    def getCurrentDir(self) -> int:
        return self.getDirectoriesKey().getCurrentDir(self.getCurrentUser(), self.getCurrentNodeName())

    def moveDir(self, ID: int, new_parent_id: int):
        dk = self.getDirectoriesKey()
        dk.move(self.getCurrentUser(), self.getCurrentNodeName(), ID, new_parent_id)
        self.saveKey(dk)

    def moveFile(self, shadowname: str, directory: int):
        fk = self.getFilesKey()
        fk.setFileDirectory(self.getCurrentUser(), self.getCurrentNodeName(), shadowname, directory)
        self.saveKey(fk)

    def rename(self, ID: int, new_name: str):
        dk = self.getDirectoriesKey()
        dk.rename(self.getCurrentUser(), self.getCurrentNodeName(), ID, new_name)
        # self.__storage.save(dk.compile(), self.fileName(dk.getFilename()) )
        self.saveKey(dk)

    def rmdir(self, ID: str):
        dk = self.getDirectoriesKey()
        dk.remove(self.getCurrentUser(), self.getCurrentNodeName(), int(ID))
        # self.__storage.save(dk.compile(), self.fileName(dk.getFilename()) )
        self.saveKey(dk)

    def remove(self, ID: str):
        if self.isFile(ID):
            fk = self.getFilesKey()
            fk.removeFile(self.getCurrentUser(), self.getCurrentNodeName(), str(ID))
            # self.__storage.save(fk.compile(), self.fileName(fk.getFilename()) )
            self.saveKey(fk)
        else:
            dk = self.getDirectoriesKey()
            dk.remove(self.getCurrentUser(), self.getCurrentNodeName(), int(ID))
            # self.__storage.save(dk.compile(), self.fileName(dk.getFilename()) )
            self.saveKey(dk)

    def cd(self, ID: int):
        dk = self.getDirectoriesKey()
        dk.cd(self.getCurrentUser(), self.getCurrentNodeName(), ID)
        # self.__storage.save(dk.compile(), self.fileName(dk.getFilename()) )
        self.saveKey(dk)

    def up(self):
        dk = self.getDirectoriesKey()
        dk.up(self.getCurrentUser(), self.getCurrentNodeName())
        # self.__storage.save(dk.compile(), self.fileName(dk.getFilename()) )
        self.saveKey(dk)

    def top(self):
        dk = self.getDirectoriesKey()
        dk.top(self.getCurrentUser(), self.getCurrentNodeName())
        # self.__storage.save(dk.compile(), self.fileName(dk.getFilename()) )
        self.saveKey(dk)

    def path(self):
        dk = self.getDirectoriesKey()
        dk.path(self.getCurrentUser(), self.getCurrentNodeName())
        # self.__storage.save(dk.compile(), self.fileName(dk.getFilename()) )
        self.saveKey(dk)

    def getDirectories(self, parent_id: int):
        dk = self.getDirectoriesKey()
        return dk.getDirectories(self.getCurrentUser(), self.getCurrentNodeName(), parent_id)

    def ls(self):
        dk = self.getDirectoriesKey()
        return dk.ls(self.getCurrentUser(), self.getCurrentNodeName())

    def addFile(self, filepath: str, status: chr, directory: int, shadowname: str = ''):
        fk = self.getFilesKey()
        shadowname = fk.addFile(self.getCurrentUser(), self.getCurrentNodeName(), filepath, status, directory, shadowname)
        self.saveKey(fk)
        return shadowname

    def getFiles(self, directory: int):
        fk = self.getFilesKey()
        return fk.getFiles(self.getCurrentUser(), self.getCurrentNodeName(), directory)

    def removeFile(self, shadowname: str):
        fk = self.getFilesKey()
        fk.removeFile(self.getCurrentUser(), self.getCurrentNodeName(), shadowname)
        self.saveKey(fk)

    def clearFilePath(self, shadowname: str):
        fk = self.getFilesKey()
        fk.clearFilePath(self.getCurrentUser(), self.getCurrentNodeName(), shadowname)
        self.saveKey(fk)

    def setFileStatus(self, shadowname: str, status: chr):
        fk = self.getFilesKey()
        fk.setFileStatus(self.getCurrentUser(), self.getCurrentNodeName(), shadowname, status)
        self.saveKey(fk)

    def setFilePaused(self, shadowname: str):
        fk = self.getFilesKey()
        fk.setFilePaused(self.getCurrentUser(), self.getCurrentNodeName(), shadowname)
        self.saveKey(fk)

    def isFilePaused(self, shadowname: str):
        fk = self.getFilesKey()
        file = fk.getFile(self.getCurrentUser(), self.getCurrentNodeName(), shadowname)
        return file['paused']

    def setFileRun(self, shadowname: str):
        fk = self.getFilesKey()
        fk.setFileRun(self.getCurrentUser(), self.getCurrentNodeName(), shadowname)
        self.saveKey(fk)

    def setFileProgress(self, shadowname: str, progress: int):
        fk = self.getFilesKey()
        fk.setProgress(self.getCurrentUser(), self.getCurrentNodeName(), shadowname, progress)
        self.saveKey(fk)
        print('+', end = " ", flush = True)
    
    def hasFiles(self) -> bool:
        key = FilesKey()
        return self.keyExists(key)

    def __zerofill(self, filename: str):
        sz = os.path.getsize(filename)
        strz = "".zfill(sz)
        
        f = open(filename, 'w')
        f.write(strz)
        f.close()

    def eraise(self, filename: str):
        self.__zerofill(filename)
        os.remove(filename)

    def eraiseAll(self):
        keysFiles = glob.glob(self.directory + "/*.json" )

        for keyFile in keysFiles:
            self.eraise(keyFile)

    def __keypair(self, entropy: int):

        return self.__keypair_seed(self.__generate_seed(entropy))

    def __keypairs(self, count: int, entropy: int):
        private_list = []
        verify_list = []
        public_list = []

        for i in range(0, count):
            keypair = self.__keypair_seed(self.__generate_seed(entropy))
            private_list.append(keypair[0])
            verify_list.append(keypair[1])
            public_list.append(keypair[2])

        return {'private': private_list, 'public': public_list, 'verify': verify_list, 'current': 0}

    def __keypair_seed(self, seed: bytes):
        SK = SigningKey(seed)
        signing_key = SK.generate()
        signing__key = signing_key.encode(encoder=Base64Encoder).decode('utf-8')
        private_key = PrivateKey(b64decode(signing__key))
        verify__key = signing_key.verify_key.encode(encoder=Base64Encoder).decode('utf-8')
        public__key = private_key.public_key.encode(encoder=Base64Encoder).decode('utf-8')

        return [signing__key, verify__key, public__key]

    def __generate_seed(self, entropy: int, len: int = 32):
        generator = prng.UhePrng()

        for i in range (0, entropy):
            rand = ''
            with open('/dev/random', 'rb') as file:
                rand = b64encode(file.read(1024)).decode('utf-8')
                file.close()

            generator.add_entropy(rand, str(uuid.getnode()))

            print('+', end = " ", flush = True)

        print("")
        
        return generator.string(len).encode(encoding = 'utf-8')

    def __generate_number_seed(self, entropy: int, len: int = 100, count: int = 25):
        generator = prng.UhePrng()

        for i in range (0, entropy):
            rand = ''
            with open('/dev/random', 'rb') as file:
                rand = b64encode(file.read(1024)).decode('utf-8')
                file.close()

            generator.add_entropy(rand, str(uuid.getnode()))

            print('+', end = " ", flush = True)

        print("")
        
        return generator.numbers(len, count)

    def __generate_word_seed(self, entropy: int, count: int = 25):
        filename = os.path.dirname(__file__) + "/../data/words"

        f = open(filename, "r")
        words = f.read()
        f.close()
        words = words.splitlines()

        seed = self.__generate_number_seed(entropy, len(words), count)

        w = []

        for num in seed:
            w.append(words[num])

        return w

    def KeyFromSeed(self, seed: str):
        generator = prng.UhePrng()

        generator.seed = seed
        numbers = generator.generate(255, 17)

        b = b''

        for num in numbers:
            b += num.to_bytes(1)

        return b64encode(b).decode(encoding = 'utf-8')

    def initSettings(self):
        key = SettingsKey()
        self.initKey(key)

    def getSettingsKey(self):
        skey = SettingsKey()
        self.loadKey(skey)
        return skey

    def getDefaultEntrophy(self) -> int:
        return self.getSettingsKey().getEntrophy()

    def getDefaultCipher(self) -> int:
        return self.getSettingsKey().getCipher()

