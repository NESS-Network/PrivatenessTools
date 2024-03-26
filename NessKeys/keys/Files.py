from NessKeys.interfaces.NessKey import NessKey
from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.DeepChecker import DeepChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException

from NessKeys.exceptions.FileNotExist import FileNotExist

import math
import random
import time
import os

class Files(NessKey):
    __files = {}

    def load(self, keydata: dict):
        map = {
            "filedata": {
                "vendor": "Privateness",
                "type": "service",
                "for": "files"
            },
            "files": dict
        }

        JsonChecker.check('Files', keydata, map)

        map = {
            'filename': str,
            'filepath': str,
            'size': int,
            'status': [str, 1],
            'size': int,
            'progress': int,
            'paused': bool,
            'directory': int
        }

        DeepChecker.check('Files (files list)', keydata, map, 4)

        self.__files = keydata["files"]

    def compile(self) -> dict:
        keydata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "service",
                "for": "files"
            },
            "files": self.__files
        }

        return keydata

    def worm(self) -> str:
        return ""
        
    def nvs(self) -> str:
        return ""

    def print(self):
        return "Privateness Files storage file"

    def filename():
        return "files.key.json"

    def getFilename(self):
        return "files.key.json"
        
    def getAllFiles(self, username: str, node_name: str):
        return self.__files[username][node_name]

        
    def getFiles(self, username: str, node_name: str, directory: int):
        fl = {}

        if username in self.__files:
            if node_name in self.__files[username]:
                for shadowname in self.__files[username][node_name]:
                    if int(self.__files[username][node_name][shadowname]['directory']) == directory:
                        fl[shadowname] = self.__files[username][node_name][shadowname]

        return fl

        
    def getAllFiles(self, username: str, node_name: str):
        fl = {}

        if username in self.__files:
            if node_name in self.__files[username]:
                for shadowname in self.__files[username][node_name]:
                    fl[shadowname] = self.__files[username][node_name][shadowname]

        return fl

    def getFile(self, username: str, node_name: str, shadowname: str) -> dict:
        if not username in self.__files:
            return False

        if not node_name in self.__files[username]:
            return False

        if not shadowname in self.__files[username][node_name]:
            return False

        return self.__files[username][node_name][shadowname]

    def getFileByFilename(self, username: str, node_name: str, filename: str):
        if not username in self.__files:
            return False

        if not node_name in self.__files[username]:
            return False

        for shadowname in self.__files[username][node_name]:
            if self.__files[username][node_name][shadowname]['filename'] == filename:
                return shadowname

        return False

    def getEncUplFileByFilename(self, username: str, node_name: str, filename: str):
        if not username in self.__files:
            return False

        if not node_name in self.__files[username]:
            return False

        for shadowname in self.__files[username][node_name]:
            if self.__files[username][node_name][shadowname]['filename'] == filename and self.__files[username][node_name][shadowname]['filename'] != shadowname and self.__files[username][node_name][shadowname]['status'] in ('u', 'e'):
                return shadowname

        return False

    def removeFile(self, username: str, node_name: str, shadowname: str):
        if not username in self.__files:
            return False

        if not node_name in self.__files[username]:
            return False

        if shadowname in self.__files[username][node_name]:
            del self.__files[username][node_name][shadowname]

    def genShadowname(self):
        alphabet_1 = ('q','w','r','t','y','p','s','d','f','g','h','k','l','z','x','c','v','b','n','m')
        alphabet_2 = ('e','u','i','o','a')

        random.seed(time.time())
        rand = math.floor(random.uniform(11, 99))

        return random.choice(alphabet_1) + \
            random.choice(alphabet_1) + \
            random.choice(alphabet_1) + \
            random.choice(alphabet_2) + '.' + str(rand)

    def addFile(self, username: str, node_name: str, filepath: str, status: chr, directory: int, shadowname: str = '') -> str:
        if shadowname == '':
            shadowname = self.genShadowname()

        filename = os.path.basename(filepath)


        if not username in self.__files:
            self.__files[username] = {}

        if not node_name in self.__files[username]:
            self.__files[username][node_name] = {}

        self.__files[username][node_name][shadowname] = {
            'filename': filename,
            'filepath': filepath,
            'size': os.path.getsize(filepath),
            'status': status,
            'progress': 0,
            'paused': False,
            'directory': directory
        }

        return shadowname

    def setProgress(self, username: str, node_name: str, shadowname: str, progress: int):
        self.__files[username][node_name][shadowname]["progress"] = progress

    def initFiles(self, username: str, node_name: str):
        if not username in self.__files:
            self.__files[username] = {}

        if not node_name in self.__files[username]:
            self.__files[username][node_name] = {}

    def setFileName(self, username: str, node_name: str, shadowname: str, filename: str):
        if not username in self.__files:
            raise FileNotExist(shadowname)

        if not node_name in self.__files[username]:
            raise FileNotExist(shadowname)

        if not shadowname in self.__files[username][node_name]:
            raise FileNotExist(shadowname)

        self.__files[username][node_name][shadowname]['filename'] = filename

    def setFileStatus(self, username: str, node_name: str, shadowname: str, status: chr):
        if not username in self.__files:
            raise FileNotExist(shadowname)

        if not node_name in self.__files[username]:
            raise FileNotExist(shadowname)

        if not shadowname in self.__files[username][node_name]:
            raise FileNotExist(shadowname)

        self.__files[username][node_name][shadowname]['status'] = status
        self.__files[username][node_name][shadowname]['paused'] = False

        # if 'paused' in self.__files[username][node_name][shadowname]:
        #     del self.__files[username][node_name][shadowname]['paused']


    def setFilePaused(self, username: str, node_name: str, shadowname: str):
        if not username in self.__files:
            raise FileNotExist(shadowname)

        if not node_name in self.__files[username]:
            raise FileNotExist(shadowname)

        if not shadowname in self.__files[username][node_name]:
            raise FileNotExist(shadowname)

        self.__files[username][node_name][shadowname]['paused'] = True

    def setFileRun(self, username: str, node_name: str, shadowname: str):
        if not username in self.__files:
            raise FileNotExist(shadowname)

        if not node_name in self.__files[username]:
            raise FileNotExist(shadowname)

        if not shadowname in self.__files[username][node_name]:
            raise FileNotExist(shadowname)

        self.__files[username][node_name][shadowname]['paused'] = False

    def setFileDirectory(self, username: str, node_name: str, shadowname: str, directory: int):
        if not username in self.__files:
            raise FileNotExist(shadowname)

        if not node_name in self.__files[username]:
            raise FileNotExist(shadowname)

        if not shadowname in self.__files[username][node_name]:
            raise FileNotExist(shadowname)

        self.__files[username][node_name][shadowname]['directory'] = directory

    def setFilePath(self, username: str, node_name: str, shadowname: str, path: str):
        if not username in self.__files:
            raise FileNotExist(shadowname)

        if not node_name in self.__files[username]:
            raise FileNotExist(shadowname)

        if not shadowname in self.__files[username][node_name]:
            raise FileNotExist(shadowname)

        self.__files[username][node_name][shadowname]['filepath'] = path

    def clearFilePath(self, username: str, node_name: str, shadowname: str):
        if not username in self.__files:
            raise FileNotExist(shadowname)

        if not node_name in self.__files[username]:
            raise FileNotExist(shadowname)

        if not shadowname in self.__files[username][node_name]:
            raise FileNotExist(shadowname)

        self.__files[username][node_name][shadowname]['filepath'] = ''
        self.__files[username][node_name][shadowname]['size'] = ''
