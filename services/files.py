from NessKeys.keys.MyNodes import MyNodes
from NessKeys.keys.Nodes import Nodes
from NessKeys.keys.Users import Users
from NessKeys.keys.Directories import Directories as DirectoriesKey
from NessKeys.keys.Files import Files as FilesKey
from NessKeys.keys.Backup import Backup as BackupKey

from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.NodeError import NodeError
from NessKeys.exceptions.AuthError import AuthError

import json
from ness.NessAuth import NessAuth
import math
import os
import time
import requests
import humanize

from NessKeys.CryptorMaker import CryptorMaker
from NessKeys.BlockCryptor import BlockCryptor
from NessKeys.TextCryptor import TextCryptor
from NessKeys.interfaces.output import output as ioutput

from framework.GLOBAL import GLOBAL

class files:
    cipher_type = 'salsa20'
    block_size = 1024**2

    def __init__(self, Users: Users, nodes: Nodes, myNodes: MyNodes, filesKey: FilesKey, directoriesKey: DirectoriesKey, backupKey: BackupKey, output: ioutput):
        self.Users = Users
        self.nodes = nodes
        self.myNodes = myNodes

        current_node = self.myNodes.getCurrentNode()

        if len(current_node) == 2:
            self.username = current_node[0]
            self.node_name = current_node[1]
        else:
            self.username = ''
            self.node_name = ''

        self.node = self.myNodes.findNode(self.username, self.node_name)

        self.auth = NessAuth()

        self.filesKey = filesKey
        self.directoriesKey = directoriesKey

        self.backupKey = backupKey

        self.output = output

    
    def fileExists(self, shadowname: str):
        return self.fileinfo(shadowname) != False


    def dir(self):
        myNode = self.myNodes.findNode(self.username, self.node_name)
        currentNode = self.nodes.findNode(self.node_name)    
        
        if currentNode == False:
            raise NodeNotFound(self.node_name)

        shadowname = myNode['shadowname']

        url = currentNode['url'] + "/files/list"

        result = self.auth.get_by_two_way_encryption(
            url, 
            'test', 
            currentNode['public'], 
            self.Users.getPrivateKey(), 
            shadowname)

        if result['result'] == 'error':
            self.err = result['error']
        else:
            if self.auth.verify_two_way_result(currentNode['verify'], result):
                files = json.loads(
                    self.auth.decrypt_two_way_result(
                        result, 
                        self.Users.getPrivateKey()))['files']

                return files
            else:
                self.err = " Verifying signature failed "

                return False

        return True

    def upload(self, filepath: str, file_shadowname: str):
        myNode = self.myNodes.findNode(self.username, self.node_name)
        currentNode = self.nodes.findNode(self.node_name) 
        filename = os.path.basename(filepath)  
        
        if currentNode == False:
            raise NodeNotFound(self.node_name)

        shadowname = myNode['shadowname']

        url = currentNode['url'] + "/files/touch"

        result = self.auth.get_by_two_way_encryption(
            url, 
            'test', 
            currentNode['public'], 
            self.Users.getPrivateKey(), 
            shadowname, 
            {'filename': self.auth.encrypt(file_shadowname, currentNode['public'])})
        
        if result['result'] == 'error':
            self.output.line(" ~~~ touch command FAILED ~~~ ")
            self.output.line(result['error'])
        else:
            if self.auth.verify_two_way_result(currentNode['verify'], result):
                self.output.line(" *** File touch *** ")

                fileinfo = json.loads(self.auth.decrypt_two_way_result(
                    result, 
                    self.Users.getPrivateKey()))

                uploaded = fileinfo['size']
                file_size = os.path.getsize(filepath)

                if uploaded >= file_size:
                    self.output.line (" *** Olready uploaded *** ")
                    return True

                blocks = math.ceil((file_size - uploaded) / self.block_size)
                blocks_total = math.ceil(file_size / self.block_size)
                blocks_uploaded = math.ceil(uploaded / self.block_size)
                url = currentNode['url'] + "/files/append/" + fileinfo['id']
                # self.output.line(fileinfo)

                file = open(filepath, "rb")
                
                self.output.line("Uploading file from " + filepath)

                for i in range(blocks):
                    if GLOBAL.halt:
                        file.close()
                        print("* Upload stopped *")
                        GLOBAL.fn_halt()
                        exit()

                    if GLOBAL.fn_paused():
                        file.close()
                        print("* Upload Paused *")
                        exit()

                    file.seek(uploaded + (self.block_size * i))
                    data = file.read(self.block_size)

                    result = self.auth.post_data_by_auth_id(
                        data, 
                        url, 
                        self.Users.getPrivateKey(), 
                        currentNode['url'], 
                        currentNode['nonce'], 
                        self.Users.getUsername(), 
                        shadowname, 
                        self.Users.getNonce())

                    if result['result'] == 'error':
                        self.output.line("")
                        self.output.line(" ~~~ Upload failed ~~~ ")
                        self.output.line(result['error'])
                        return False
                    else:
                        if (blocks_uploaded + i) > 0:
                            GLOBAL.fn_progress(round((blocks_uploaded + i)*100/blocks_total))
                        # self.output.out("+")
                    # time.sleep(1)

                file.close()

                GLOBAL.fn_progress(100)

                self.output.line ('')
                self.output.line (" *** UPLOADED *** ")
                self.output.line ("File shadowname: " + file_shadowname)
            else:
                self.output.line(" ~~~ list command FAILED ~~~ ")
                self.output.line(" Verifying signature failed ")

                return False

        return True

    def __fileinfo(self, file_id: str):
        myNode = self.myNodes.findNode(self.username, self.node_name)
        currentNode = self.nodes.findNode(self.node_name) 
        
        if currentNode == False:
            raise NodeNotFound(self.node_name)

        shadowname = myNode['shadowname']

        url = currentNode['url'] + "/files/fileinfo"

        result = self.auth.get_by_two_way_encryption(
            url, 'test', 
            currentNode['public'], 
            self.Users.getPrivateKey(), 
            shadowname, 
            {'file_id': file_id})

        if result['result'] == 'error':
            self.output.line(" ~~~ fileinfo command FAILED ~~~ ")
            self.output.line(result['error'])
        else:
            if self.auth.verify_two_way_result(currentNode['verify'], result):

                fileinfo = json.loads(self.auth.decrypt_two_way_result(result, self.Users.getPrivateKey()))

                fileinfo['dl'] = currentNode['url'] + "/files/download/" + shadowname + "/" + fileinfo['id'] + "/" + self.auth.auth_id(self.Users.getPrivateKey(), currentNode['url'], currentNode["nonce"], self.Users.getUsername(), self.Users.getNonce())

                fileinfo['pub'] = currentNode['url'] + "/files/pub/" + fileinfo['id'] + "-" + shadowname + "-" + self.auth.alternative_id(self.Users.getPrivateKey(), currentNode['url'], currentNode["nonce"], self.Users.getUsername(), self.Users.getNonce())

                return fileinfo
            else:
                self.output.line(" ~~~ fileinfo command FAILED ~~~ ")
                self.output.line(" Verifying signature failed ")

                return False

        return True

    def fileinfo(self, shadowname: str):
        dir = self.dir()

        if not shadowname in dir:
            return False

        info_node = self. __fileinfo(dir[shadowname]['id'])
        all_files = self.filesKey.getAllFiles(self.username, self.node_name)

        if shadowname in all_files:
            info_local = all_files[shadowname]
        else:
            info_local = {
                'filename': shadowname,
                'size': 0,
                'filepath': '',
                'status': 'n',
            }

        fileinfo = {
            'id': info_node['id'],
            'filename': info_local['filename'],
            'shadowname': shadowname,
            'status': self.__status(info_local),
            'size_local': info_local['size'],
            'size_remote': humanize.naturalsize(info_node['size']),
            'filepath': info_local['filepath'],
            'pub': info_node['pub']
        }

        if fileinfo['size_local'] != '':
            fileinfo['size_local'] = humanize.naturalsize(fileinfo['size_local'])

        return fileinfo

    def quota(self):
        myNode = self.myNodes.findNode(self.username, self.node_name)
        currentNode = self.nodes.findNode(self.node_name) 
        
        if currentNode == False:
            raise NodeNotFound(self.node_name)

        shadowname = myNode['shadowname']

        url = currentNode['url'] + "/files/quota"

        result = self.auth.get_by_two_way_encryption(url, 'test', currentNode['public'], self.Users.getPrivateKey(), shadowname)

        if result['result'] == 'error':
            self.output.line(" ~~~ quota command FAILED ~~~ ")
            self.output.line(result['error'])
            return False
        else:
            if self.auth.verify_two_way_result(currentNode['verify'], result):
                print(" *** User file storage quota *** ")
                quota = json.loads(self.auth.decrypt_two_way_result(result, self.Users.getPrivateKey()))
                return quota['quota']
            else:
                self.output.line(" ~~~ quota command FAILED ~~~ ")
                self.output.line(" Verifying signature failed ")

                return False

    def __download(self, file_id: str, real_filename: str, path: str = ''):
        myNode = self.myNodes.findNode(self.username, self.node_name)
        currentNode = self.nodes.findNode(self.node_name)    
        url_dl = currentNode['url'] + "/files/download/" + file_id
        
        if currentNode == False:
            raise NodeNotFound(self.node_name)

        shadowname = myNode['shadowname']

        fileinfo = self.__fileinfo(file_id)

        filename = fileinfo['filename']

        if path != '':
            if path[-1] != '/':
                path = path + '/'
            filename = path + filename
            real_filename = path + real_filename

        size = fileinfo['size']

        f = open(real_filename, 'ab')
        pos = f.tell()
        # print (size, pos, filename, real_filename)
        blocks_downloaded = round(pos / self.block_size)

        headers = {'Range': 'bytes=' + str(pos) + '-'}

        responce = self.auth.get_responce_by_auth_id(
            url_dl, 
            self.Users.getPrivateKey(), 
            currentNode['url'], 
            currentNode['nonce'], 
            self.Users.getUsername(), 
            shadowname, 
            self.Users.getNonce(), 
            headers)
        # self.output.line(responce.status_code)
        i = 0
        for block in responce.iter_content(chunk_size = self.block_size):
            if GLOBAL.halt:
                f.close()
                print("* Download stopped *")
                GLOBAL.fn_halt()
                exit()

            if GLOBAL.fn_paused():
                f.close()
                print("* Download Paused *")
                exit()
                
            f.write(block)
            GLOBAL.fn_progress( round( ((blocks_downloaded + i) * self.block_size * 100) / size ) )
            i += 1

            # time.sleep(1)

        GLOBAL.fn_progress(100)

        f.close()

        # os.rename(filename, real_filename)

        self.output.line("")
        self.output.line(" *** DOWNLOAD OK *** ")

        return True

    def __remove(self, file_id: str):
        myNode = self.myNodes.findNode(self.username, self.node_name)
        currentNode = self.nodes.findNode(self.node_name)
        
        if currentNode == False:
            raise NodeNotFound(self.node_name)

        shadowname = myNode['shadowname']

        url = currentNode['url'] + "/files/remove"

        result = self.auth.get_by_two_way_encryption(
            url, 
            'test', 
            currentNode['public'], 
            self.Users.getPrivateKey(), 
            shadowname,
            {'file_id': file_id})
        
        if result['result'] == 'error':
            self.output.line(" ~~~ remove command FAILED ~~~ ")
            self.output.line(result['error'])
        else:
            if self.auth.verify_two_way_result(currentNode['verify'], result):
                self.output.line(" *** File removed *** ")
                return True
            else:
                self.output.line(" ~~~ remove command FAILED ~~~ ")
                self.output.line(" Verifying signature failed ")

                return False


    def download(self, shadowname: str, path: str = ''):
        file = self.filesKey.getFile(self.username, self.node_name, shadowname)
        dir = self.dir()

        if shadowname in dir:

            if shadowname != file['filename']:          
                decr_path = os.getcwd() + '/_dec/'
                self.__download(dir[shadowname]['id'], file['filename'], decr_path)
            else:
                self.__download(dir[shadowname]['id'], file['filename'], path)

            return True
        else:
            return False


    def remove(self, shadowname: str):
        dir = self.dir()

        if shadowname in dir:
            self.__remove(dir[shadowname]['id'])
            return True
        else:
            return False


    def removeLocal(self, shadowname: str):
        file = self.filesKey.getFile(self.username, self.node_name, shadowname)
        if os.path.exists(file['filepath']):
            os.remove(file['filepath'])

    def __status(self, file: dict):
        if file['status'] == 'c':
            return 'Created'
        elif file['status'] == 'e':
            return 'Encrypting ({}%)'.format(file['progress'])
        elif file['status'] == 'u':
            return 'Uploading ({}%)'.format(file['progress'])
        elif file['status'] == 'n':
            return 'On Node'
        elif file['status'] == 'w':
            return 'Downloading ({}%)'.format(file['progress'])
        elif file['status'] == 'd':
            return 'Decrypting ({}%)'.format(file['progress'])


    def ls(self):
        myNode = self.myNodes.findNode(self.username, self.node_name)
        currentNode = self.nodes.findNode(self.node_name)
        currentDir = self.directoriesKey.getCurrentDir(self.username, self.node_name)
        currentDirName = self.directoriesKey.getCurrentName(self.username, self.node_name)

        if currentNode == False:
            raise NodeNotFound(self.node_name)

        node_shadowname = myNode['shadowname']

        dir = self.dir()

        if dir != False:
            files = self.filesKey.getFiles(self.username, self.node_name, currentDir)
            directories = self.directoriesKey.ls(self.username, self.node_name)
            result = {}
            
            for id in directories:
                result[id] = directories[id]
                result[id]['filename'] = '[' + directories[id]['name'] + ']'
                result[id]['size'] = ''
                result[id]['pub'] = ''
                result[id]['status'] = ''

            for shadowname in files:
                file = files[shadowname]
                if shadowname in dir:
                    dirf = dir[shadowname]

                    if shadowname == file['filename']:
                        pub = currentNode['url'] + "/files/pub/" + dirf['id'] + "-" + node_shadowname + "-" + self.auth.alternative_id(self.Users.getPrivateKey(), currentNode['url'], currentNode["nonce"], self.Users.getUsername(), self.Users.getNonce())
                    else:
                        pub = ""

                    file['size'] = humanize.naturalsize(dirf['size'])
                    file['pub'] = pub
                else:
                    file['size'] = ''
                    file['pub'] = ''

                file['status'] = self.__status(file)

                result[shadowname] = file

            self.output.line(" *** Contents of {}  ".format(currentDirName))

            return result
        else:
            return False


    def raw(self):
        return self.dir()

    def jobs(self):
        myNode = self.myNodes.findNode(self.username, self.node_name)
        currentNode = self.nodes.findNode(self.node_name)
        
        if currentNode == False:
            raise NodeNotFound(self.node_name)

        dir = self.dir()

        node_shadowname = myNode['shadowname']

        files = self.filesKey.getAllFiles(self.username, self.node_name)

        result = {}

        for shadowname in files:
            file = files[shadowname]
            if file['paused'] or not file['progress'] in (0, 100):

                if shadowname == file['filename'] and shadowname in dir:
                    dirf = dir[shadowname]
                    pub = currentNode['url'] + "/files/pub/" + dirf['id'] + "-" + node_shadowname + "-" + self.auth.alternative_id(self.Users.getPrivateKey(), currentNode['url'], currentNode["nonce"], self.Users.getUsername(), self.Users.getNonce())
                else:
                    pub = "-"


                if file['paused']:
                    action = '[  ||| PAUSED ||| ]'
                else:
                    action = '[ >>> RUNNING >>> ]'

                file['action'] = action
                file['status'] = self.__status(file)


                if shadowname in dir:
                    dirf = dir[shadowname]
                    file['pub'] = pub
                    file['size'] = humanize.naturalsize(dirf['size'])
                else:
                    file['pub'] = '-'
                    file['size'] = '-'

                result[shadowname] = file

        return result

    def encrypt(self, filepath: str, shadowname: str):
        file = self.filesKey.getFile(self.username, self.node_name, shadowname)
        cryptor = CryptorMaker.make(self.node['cipher'])

        filename = os.path.basename(filepath)
        filename_out = os.getcwd() + '/_enc/' + filename
        
        bc = BlockCryptor(cryptor, bytes(self.node['key'][:cryptor.getBlockSize()], 'utf8'), self.output, self.block_size)

        self.output.line("Encrypting file from {} to {}".format(filepath, filename_out))
        bc.encrypt(filepath, filename_out)
        self.output.line ("")
        self.output.line (" *** ENCRYPTED *** ")

        return filename_out


    def decrypt(self, shadowname: str, path: str = ''):
        file = self.filesKey.getFile(self.username, self.node_name, shadowname)
        dir = self.dir()

        if shadowname in dir:
            cryptor = CryptorMaker.make(self.node['cipher'])            
            
            decr_path = os.getcwd() + '/_dec/'

            if path != '' and path[-1] != '/':
                path = path + '/'

            from_filename = decr_path + file['filename']
            to_filename = path + file['filename']
            
            bc = BlockCryptor(cryptor, bytes(self.node['key'][:cryptor.getBlockSize()], 'utf8'), self.output, self.block_size)

            self.output.line("Decrypting file from {} to {}".format(from_filename, to_filename))
            bc.decrypt(from_filename, to_filename)
            self.output.line ("")
            self.output.line (" *** DECRYPTED *** ")
            
            os.remove(from_filename)

            return True
        else:
            return False

    def uploadEncryptString(self, data: str, file_shadowname: str):
        myNode = self.myNodes.findNode(self.username, self.node_name)
        currentNode = self.nodes.findNode(self.node_name)
        
        if currentNode == False:
            raise NodeNotFound(self.node_name)

        user_shadowname = myNode['shadowname']

        url = currentNode['url'] + "/files/rewrite"

        result = self.auth.get_by_two_way_encryption(
            url, 
            'test', 
            currentNode['public'], 
            self.Users.getPrivateKey(), 
            user_shadowname, 
            {'filename': self.auth.encrypt(file_shadowname, currentNode['public'])})

        if result['result'] == 'error':
            self.output.line(" ~~~ touch command FAILED ~~~ ")
            self.output.line(result['error'])
        else:
            if self.auth.verify_two_way_result(currentNode['verify'], result):

                fileinfo = json.loads(self.auth.decrypt_two_way_result(
                    result, 
                    self.Users.getPrivateKey()))

                cryptor = CryptorMaker.make(self.backupKey.getCipher())
                tc = TextCryptor(cryptor, bytes(self.backupKey.getKey(), 'utf8') [:cryptor.getBlockSize()])
                data = tc.encrypt(bytes(data, 'utf8'))

                url = currentNode['url'] + "/files/append/" + fileinfo['id']

                result = self.auth.post_data_by_auth_id(
                    data, 
                    url, 
                    self.Users.getPrivateKey(), 
                    currentNode['url'], 
                    currentNode['nonce'], 
                    self.Users.getUsername(), 
                    user_shadowname, 
                    self.Users.getNonce())

    # def downloadDecryptStringFromUrl(self, url: str) -> str:
    #     myNode = self.myNodes.findNode(self.username, self.node_name)
    #     currentNode = self.nodes.findNode(self.node_name)
        
    #     if currentNode == False:
    #         raise NodeNotFound(self.node_name)

    #     shadowname = myNode['shadowname']

    #     headers = {}

    #     responce = self.auth.get_responce_by_auth_id(
    #         url, 
    #         self.Users.getPrivateKey(), 
    #         currentNode['url'], 
    #         currentNode['nonce'], 
    #         self.Users.getUsername(), 
    #         shadowname, 
    #         self.Users.getNonce(), 
    #         headers)
        

    #     cryptor = CryptorMaker.make(self.backupKey.getCipher())
    #     tc = TextCryptor(cryptor, bytes(self.backupKey.getKey(), 'utf8') [:cryptor.getBlockSize()])
    #     data = tc.decrypt(responce.content)

    #     return  data.decode('utf-8')

    def downloadDecryptString(self, file_shadowname: str) -> str:
        myNode = self.myNodes.findNode(self.username, self.node_name)
        currentNode = self.nodes.findNode(self.node_name)    

        fileinfo = self.fileinfo(file_shadowname)

        url_dl = currentNode['url'] + "/files/download/" + fileinfo['id']
        
        if currentNode == False:
            raise NodeNotFound(self.node_name)

        shadowname = myNode['shadowname']

        headers = {}

        responce = self.auth.get_responce_by_auth_id(
            url_dl, 
            self.Users.getPrivateKey(), 
            currentNode['url'], 
            currentNode['nonce'], 
            self.Users.getUsername(), 
            shadowname, 
            self.Users.getNonce(), 
            headers)
        

        cryptor = CryptorMaker.make(self.backupKey.getCipher())
        tc = TextCryptor(cryptor, bytes(self.backupKey.getKey(), 'utf8') [:cryptor.getBlockSize()])
        data = tc.decrypt(responce.content)

        return  data.decode('utf-8')