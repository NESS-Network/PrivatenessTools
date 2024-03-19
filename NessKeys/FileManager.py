from NessKeys.KeyManager import KeyManager
import NessKeys.Prng as prng

from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.NodeNotSelected import NodeNotSelected
from NessKeys.exceptions.FileNotExist import FileNotExist

from base64 import b64encode
from base64 import b64decode
import uuid
import os

from services.node import node
from services.files import files

from framework.GLOBAL import GLOBAL

class FileManager:

    def __init__(self, KeyManager: KeyManager, NodesService: node, FilesService: files):
        self.KeyManager = KeyManager
        self.NodesService = NodesService
        self.FilesService = FilesService

    def join(self, username: str = "", node_url: str = ""):        
        self.KeyManager.initKeys()
        
        if username != "":
            self.KeyManager.changeCurrentUser(username)

        if not self.KeyManager.isNodeInNodesList(node_url):
            raise NodeNotFound(node_url)

        shadowname = self.NodesService.joined(node_url)

        if shadowname == False:
            entropy = self.KeyManager.getDefaultEntrophy()

            print(" *** Generating keys for node {} ...".format(node_url))

            generator = prng.UhePrng()

            for i in range (1, entropy):
                rand = ''
                with open('/dev/random', 'rb') as file:
                    rand = b64encode(file.read(1024)).decode('utf-8')
                    file.close()

                generator.add_entropy(rand, str(uuid.getnode()))

                print('+', end = " ", flush = True)

            print("")

            cipher =  self.KeyManager.getDefaultCipher()

            if cipher == 'salsa20':
                key = generator.string(32)
            elif cipher == 'aes':
                key = generator.string(16)

            for i in range (1, entropy):
                rand = ''
                with open('/dev/random', 'rb') as file:
                    rand = b64encode(file.read(1024)).decode('utf-8')
                    file.close()

                generator.add_entropy(rand, str(uuid.getnode()))

                print('+', end = " ", flush = True)

            print("")

            fskey = generator.string(16)
            
            shadowname = self.NodesService.join(node_url)

            self.KeyManager.saveCurrentNode(node_url, shadowname, b64encode(key.encode()).decode('utf-8'), b64encode(fskey.encode()).decode('utf-8'), cipher)


        self.KeyManager.changeCurrentNode(node_url)

        print("Node URL {} is joined with SHADOWNAME {}".format(node_url, shadowname))

    def ls(self):
        self.KeyManager.initFilesAndDirectories()

        if self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            self.FilesService.ls()
        else:
            raise NodeNotSelected()
    def jobs(self):
        self.KeyManager.initFilesAndDirectories()

        if self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            self.FilesService.jobs()
        else:
            raise NodeNotSelected()

    def raw(self):
        self.KeyManager.initFilesAndDirectories()

        if self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            self.FilesService.raw()
        else:
            raise NodeNotSelected()

    def tree(self):
        self.KeyManager.initFilesAndDirectories()
        return self.KeyManager.tree()

    def upload(self, filepath: str):
        node_name = self.KeyManager.getCurrentNodeName()

        if not os.path.exists(filepath):
            raise FileNotExist(filepath)

        if not self.NodesService.joined(node_name):
            raise NodeNotSelected(node_name)
        
        self.KeyManager.initFilesAndDirectories()
        shadowname = os.path.basename(filepath)

        def ex_progress(km, shadowname):
            return lambda progress : km.setFileProgress(shadowname, progress)

        GLOBAL.fn_progress = ex_progress(self.KeyManager, shadowname)

        def ex_halt(km, shadowname):
            return lambda : km.setFilePaused(shadowname)

        GLOBAL.fn_halt = ex_halt(self.KeyManager, shadowname)

        def is_paused(km, shadowname):
            def ret():
                return km.isFilePaused(shadowname)

            return ret

        GLOBAL.fn_paused = is_paused(self.KeyManager, shadowname)

        self.KeyManager.addFile(filepath, 'u', self.KeyManager.getCurrentDir(), shadowname)
        self.FilesService.upload(filepath, shadowname, fn_progress, fn_halt)
        self.KeyManager.setFileStatus(shadowname, 'n')

    def download(self, shadowname: str, path: str = ""):
        node_name = self.KeyManager.getCurrentNodeName()

        if not self.NodesService.joined(node_name):
            raise NodeNotSelected()

        self.KeyManager.initFilesAndDirectories()

        file = self.KeyManager.getFile(shadowname)

        if file == False:
            raise FileNotExist(shadowname)

        def ex_progress(km, shadowname):
            return lambda progress : km.setFileProgress(shadowname, progress)

        GLOBAL.fn_progress = ex_progress(self.KeyManager, shadowname)

        def ex_halt(km, shadowname):
            return lambda : km.setFilePaused(shadowname)

        GLOBAL.fn_halt = ex_halt(self.KeyManager, shadowname)

        def is_paused(km, shadowname):
            def ret():
                return km.isFilePaused(shadowname)

            return ret

        GLOBAL.fn_paused = is_paused(self.KeyManager, shadowname)

        self.KeyManager.setFileStatus(shadowname, 'w')

        if file['filename'] == shadowname:
            self.FilesService.download(shadowname, path)
        else:
            self.FilesService.download(shadowname)

        if file['filename'] != shadowname:
            self.KeyManager.setFileStatus(shadowname, 'd')
            self.FilesService.decrypt(shadowname, path)

        self.KeyManager.setFileStatus(shadowname, 'n')

    def UploadEncrypt(self, filepath: str):
        node_name = self.KeyManager.getCurrentNodeName()

        if not os.path.exists(filepath):
            raise FileNotExist(filepath)

        if not self.NodesService.joined(node_name):
            raise NodeNotSelected(node_name)

        self.KeyManager.initFilesAndDirectories()

        filename = os.path.basename(filepath)

        shadowname = self.KeyManager.findEncUplFile(filename)

        if shadowname == False:
            shadowname = self.KeyManager.addFile(filepath, 'e', self.KeyManager.getCurrentDir())

        def ex_progress(km, shadowname):
            return lambda progress : km.setFileProgress(shadowname, progress)

        GLOBAL.fn_progress = ex_progress(self.KeyManager, shadowname)

        def ex_halt(km, shadowname):
            return lambda : km.setFilePaused(shadowname)

        GLOBAL.fn_halt = ex_halt(self.KeyManager, shadowname)

        def is_paused(km, shadowname):
            def ret():
                return km.isFilePaused(shadowname)

            return ret

        GLOBAL.fn_paused = is_paused(self.KeyManager, shadowname)

        self.KeyManager.setFileStatus(shadowname, 'e')
        encpath = self.FilesService.encrypt(filepath, shadowname)
        self.KeyManager.setFileStatus(shadowname, 'u')
        self.FilesService.upload(encpath, shadowname)
        self.KeyManager.setFileStatus(shadowname, 'n')
        os.remove(encpath)

        return encpath

    def pauseJob(self, shadowname: str):
        self.KeyManager.setFilePaused(shadowname)

    def runJob(self, shadowname: str):
        file = self.KeyManager.getFile(shadowname)

        if file['status'] == 'u' :
            if shadowname == file['filename']:
                self.upload(file['filepath'])
            else:
                self.UploadEncrypt(file['filepath'])
        elif file['status'] == 'e':
            self.UploadEncrypt(file['filepath'])
        elif file['status'] in ('w','d'):
            self.download(shadowname)

        print("*** Job on file {} is paused".format(shadowname))

    def saveFilesAndDirectoriesFile(self):
        pass