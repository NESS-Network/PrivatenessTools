from NessKeys.KeyManager import KeyManager
import NessKeys.Prng as prng

from NessKeys.interfaces.NessKey import NessKey
from NessKeys.keys.Files import Files as FilesKey
from NessKeys.keys.Directories import Directories as DirectoriesKey
from NessKeys.keys.Encrypted import Encrypted

from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.NodeNotSelected import NodeNotSelected
from NessKeys.exceptions.FileNotExist import FileNotExist
from NessKeys.exceptions.DirectoryNotEmpty import DirectoryNotEmpty

from base64 import b64encode
from base64 import b64decode
import uuid
import os
import json
from prettytable import PrettyTable
import humanize
from typing import Callable

from services.node import node
from services.files import files

from framework.GLOBAL import GLOBAL

class FileManager:

    def __init__(self, KeyManager: KeyManager, NodesService: Callable, FilesService: Callable):
        self.KeyManager = KeyManager
        self.fnNodesService = NodesService
        self.fnFilesService = FilesService
        self.NodesService = self.fnNodesService()
        self.FilesService = self.fnFilesService()

    def join(self, username: str = "", node_url: str = ""):        
        self.initKeys()
        
        if username != "":
            self.KeyManager.changeCurrentUser(username)
        else:
            username = self.KeyManager.getCurrentUser()

        if not self.KeyManager.isNodeInNodesList(node_url):
            raise NodeNotFound(node_url)

        shadowname = self.NodesService.joined(node_url)

        if shadowname == False:
            shadowname = self.NodesService.join(node_url)

        if not self.KeyManager.isNodeInMyNodes(username, node_url):
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
            

            self.KeyManager.saveCurrentNode(node_url, shadowname, b64encode(key.encode()).decode('utf-8'), b64encode(fskey.encode()).decode('utf-8'), cipher)


        self.KeyManager.changeCurrentNode(node_url)

        print("Node URL {} is joined with SHADOWNAME {}".format(node_url, shadowname))

    def ls(self):
        if not self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            raise NodeNotSelected()

        files = self.FilesService.ls()

        if files != False:
            t = PrettyTable(['Shadowname', 'Filename', 'Size', 'Status', 'Share'])

            for shadowname in files:
                file = files[shadowname]
                t.add_row([shadowname, file['filename'], file['size'], file['status'], file['pub']])

            t.align = 'l'

            print(t)

    def raw(self):
        if not self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            raise NodeNotSelected()

        files = self.FilesService.raw()

        if files != False:
            t = PrettyTable(['Filename', 'ID', 'Size'])
            t.align = 'l'

            for filename in files:
                t.add_row([filename, files[filename]['id'], files[filename]['size']])

            print(t)

    def cd(self, ID: int):
        if self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            self.KeyManager.cd(ID)
        else:
            raise NodeNotSelected()

    def up(self):
        if self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            self.KeyManager.up()
        else:
            raise NodeNotSelected()

    def top(self):
        if self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            self.KeyManager.top()
        else:
            raise NodeNotSelected()

    def moveDir(self, ID: int, new_parent_id: int):
        if self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            self.KeyManager.moveDir(ID, new_parent_id)
        else:
            raise NodeNotSelected()   

    def moveFile(self, shadowname: str, directory: int):
        if self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            self.KeyManager.moveFile(shadowname, directory)
        else:
            raise NodeNotSelected()   

    def move(self, ID: str, directory: int):
        dir = self.KeyManager.getDirectory(directory)

        if dir == False:
            raise DirectoryNotEmpty(dir['name'])

        if self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            if self.KeyManager.isFile(ID):
                self.KeyManager.moveFile(ID, directory)
            else:
                self.KeyManager.moveDir(int(ID), directory)

    def fileinfo(self, shadowname: str):
        fileinfo =  self.FilesService.fileinfo(shadowname)

        if fileinfo != False:
            print(" *** fileinfo *** ")
            t = PrettyTable(['Param', 'value'])

            t.add_row(["File ID", fileinfo['id']])
            t.add_row(["Filename", fileinfo['filename']])
            t.add_row(["Shadowname", fileinfo['shadowname']])
            t.add_row(["Status", fileinfo['status']])
            t.add_row(["Filesize (local)", fileinfo['size_local']])
            t.add_row(["Filesize (remote)", fileinfo['size_remote']])
            t.add_row(["Filepath (local)", fileinfo['filepath']])
            t.add_row(["Public link", fileinfo['pub']])

            t.align = 'l'
            print(t)
        else:
            print("File {} does not exist".format(shadowname))

    def remove(self, file_shadowname: str):
        if self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            self.FilesService.remove(file_shadowname)
            self.KeyManager.removeFile(file_shadowname)

    def removeLocal(self, file_shadowname: str):
        if self.NodesService.joined(km.getCurrentNodeName()):
            if self.KeyManager.getFile(file_shadowname) == False:
                raise FileNotExist(file_shadowname)
            
            self.FilesService.removeLocal(file_shadowname)
            self.KeyManager.clearFilePath(file_shadowname)

    def rename(self, ID: int, new_name: str):
        if self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            self.KeyManager.rename(ID, new_name)
        else:
            raise NodeNotSelected()   


    def mkdir(self, parent_id: int, name: str) -> int:
        if self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            self.KeyManager.mkdir(parent_id, name)
        else:
            raise NodeNotSelected()    

    def rmdir(self, ID: str):
        if self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            if int(ID) == 0:
                return False

            if len(self.KeyManager.getFiles(ID)) > 0:
                dir = self.KeyManager.getDirectory(ID)
                raise DirectoryNotEmpty(dir['name'])

            if len(self.KeyManager.getDirectories(ID)) > 0:
                dir = self.KeyManager.getDirectory(ID)
                raise DirectoryNotEmpty(dir['name'])

            self.KeyManager.rmdir(ID)
        else:
            raise NodeNotSelected()         

    def jobs(self):
        if self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            jobs = self.FilesService.jobs()

            t = PrettyTable(['Action', 'Shadowname', 'Filename', 'Size', 'Status', 'Share'])
            t.align = 'l'

            for shadowname in jobs:
                job = jobs[shadowname]
                t.add_row([job['action'], shadowname, job['filename'], job['size'], job['status'], job['pub']])

            print(t)
        else:
            raise NodeNotSelected()



    def quota(self):
        if not self.NodesService.joined(self.KeyManager.getCurrentNodeName()):
            raise NodeNotSelected()

        quota = self.FilesService.quota()

        if quota != False:
            t = PrettyTable(['Param', 'value'])
            t.align = 'l'
            t.add_row(["Total", humanize.naturalsize(quota['total'])])
            t.add_row(["Used", humanize.naturalsize(quota['used'])])
            t.add_row(["Free", humanize.naturalsize(quota['free'])])

            print(t)

        return True

    def tree(self):
        return self.KeyManager.tree()

    def upload(self, filepath: str):
        node_name = self.KeyManager.getCurrentNodeName()

        if not os.path.exists(filepath):
            raise FileNotExist(filepath)

        if not self.NodesService.joined(node_name):
            raise NodeNotSelected(node_name)
        
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
        self.FilesService.upload(filepath, shadowname)
        self.KeyManager.setFileStatus(shadowname, 'n')

        return shadowname

    def download(self, shadowname: str, path: str = ""):
        node_name = self.KeyManager.getCurrentNodeName()

        if not self.NodesService.joined(node_name):
            raise NodeNotSelected()

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

        return shadowname

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

    def filesKeyExist(self):
        files_key_shadowname = self.KeyManager.getBackupKey().getFilesShadowname()
        return self.FilesService.fileExists(files_key_shadowname)

    def dirsKeyExist(self):
        dirs_key_shadowname = self.KeyManager.getBackupKey().getDirsShadowname()
        return self.FilesService.fileExists(dirs_key_shadowname)

    def uploadEncryptKey(self, key: NessKey, shadowname: str = ""):
        if shadowname == "":
            shadowname = self.KeyManager.genShadowname()

        keydata = key.compile()
        keydata = json.dumps(keydata)
        self.FilesService.uploadEncryptString(keydata, shadowname)

        return shadowname

    def uploadEncryptFilesKey(self):
        shadowname = self.KeyManager.getBackupKey().getFilesShadowname()
        self.uploadEncryptKey( self.KeyManager.getFilesKey(), shadowname)

    def uploadEncryptDirsKey(self):
        shadowname = self.KeyManager.getBackupKey().getDirsShadowname()
        self.uploadEncryptKey( self.KeyManager.getDirectoriesKey(), shadowname)

    def uploadEncryptEncryptedKey(self, key: Encrypted):
        return self.uploadEncryptKey(key)

    def downoadDeryptEncryptedKey(self, url: str) -> Encrypted:
        keydata = self.FilesService.downloadDecryptStringFromUrl(url)
        keydata = json.loads(keydata)

        key = self.KeyManager.createEncryptedKey('aes')
        key.load(keydata)
        self.KeyManager.saveKey(key)

    def downoadDeryptFilesKey(self):
        shadowname = self.KeyManager.getBackupKey().getFilesShadowname()
        keydata = self.FilesService.downloadDecryptString(shadowname)
        keydata = json.loads(keydata)

        key = self.KeyManager.getFilesKey()
        key.load(keydata)
        self.KeyManager.saveKey(key)

    def downoadDeryptDirsKey(self):
        shadowname = self.KeyManager.getBackupKey().getDirsShadowname()
        keydata = self.FilesService.downloadDecryptString(shadowname)
        keydata = json.loads(keydata)

        key = self.KeyManager.getDirectoriesKey()
        key.load(keydata)
        self.KeyManager.saveKey(key)

    def remoteFilesFileExist(self):
        shadowname = self.KeyManager.getBackupKey().getFilesShadowname()
        return self.FilesService.fileExists(shadowname)

    def remoteDirsFileExist(self):
        shadowname = self.KeyManager.getBackupKey().getDirsShadowname()
        return self.FilesService.fileExists(shadowname)

    def saveFilesAndDirectoriesFile(self):
        self.uploadEncryptDirsKey()
        self.uploadEncryptFilesKey()

    def initDirectoriesAndFilesKey(self):
        recreate = False

        if self.KeyManager.hasDirectoriesKey():
            self.KeyManager.refreshDirectoriesKey()
        else:
            if self.remoteDirsFileExist():
                self.downoadDeryptDirsKey()
            else:
                self.KeyManager.initDirectoriesKey()

            recreate = True

        if self.KeyManager.hasFilesKey():
            self.KeyManager.refreshFilesKey()
        else:
            if self.remoteFilesFileExist():
                self.downoadDeryptFilesKey()
            else:
                self.KeyManager.initFilesKey()

            recreate = True

        if recreate:
            self.NodesService = self.fnNodesService()
            self.FilesService = self.fnFilesService()


    def initKeys(self):
        self.KeyManager.initSettings()
        self.KeyManager.initMyNodes()

        self.initDirectoriesAndFilesKey()

    def saveKeys(self):
        self.saveFilesAndDirectoriesFile()