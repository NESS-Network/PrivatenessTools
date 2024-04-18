import os
import sys
from base64 import b64encode
from base64 import b64decode
import json
import urllib.parse
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import datetime
import requests

import uuid
import NessKeys.Prng as prng
from framework.Container import Container
from framework.ARGS import ARGS

from NessKeys.keys.Encrypted import Encrypted
from NessKeys.keys.Backup import Backup

class Backup:

    def __manual(self):
        print("*** PrivateNess keys BACKUP")
        print("### Show backup SEED")
        print(" ./backup seed")
        print("### Show backup ADDRESS")
        print(" ./backup address")
        print("### Do backup to selected NODE or to FILE")
        print(" ./backup backup [filename]")
        print("### Restore backup from current NODE or from FILE")
        print(" ./backup restore [filename]")

    def process(self):
        if ARGS.args(['seed']):
            manager = Container.KeyManager()
            bkey = manager.getBackupKey()

            if bkey == False:
                print ("Backup file not found")
            else:
                print(bkey.getSeed())
        elif ARGS.args(['address']):
            manager = Container.KeyManager()
            bkey = manager.getBackupKey()

            if bkey == False:
                print ("Backup file not found")
            else:
                print(bkey.getAddress())
        elif ARGS.args(['backup']):
            fm = Container.FileManager()
            manager = Container.KeyManager()
            bkey = manager.getBackupKey()


            if bkey.getType() == 'node':
                ekey = manager.packKeysKey(manager.getLocalKeyFiles(), bkey.getCipher(), bytes(bkey.getKey(), 'utf8'))
                shadowname = fm.uploadEncryptEncryptedKey(ekey)
                fileinfo = fm.FilesService.fileinfo(shadowname)
                bkey.setAddress(fileinfo['pub'])
                print (" *** Backup link: " + fileinfo['pub'])
                manager.saveKey(bkey)
            else:
                dt = datetime.datetime.now()
                time = dt.strftime("%Y-%m-%d %H:%M:%S")
                filename = "Backup " + time +".json"
                manager.packKeys(manager.getLocalKeyFiles(), bkey.getCipher(), bytes(bkey.getKey(), 'utf8'), filename)


        elif ARGS.args(['restore', str]):
            manager = Container.KeyManager()
            filename = sys.argv[2]

            if not os.path.exists(filename):
                print("File {} does not exist".format(filename))
                return False

            seed = input("Input seed:")

            key = manager.KeyFromSeed(seed.strip())

            if manager.unpackKeys(key, filename):
                print (" *** Keys unpacked to {} directory".format(manager.directory))

        elif ARGS.args(['restore']):
            manager = Container.KeyManager()
            
            address = input("Input address:")

            seed = input("Input seed:")

            key = manager.KeyFromSeed(seed.strip())

            encr = requests.get(address).content

            try:
                ekey_text = manager.unpack(encr, key)
            except Exception as e:
                print(" ~~~ Decryption error ~~~ ")
                print("Check URL address and seed")
                exit(1)

            ekey = manager.EncrypedKeyFromString(ekey_text)

            if manager.unpackKeysFromKey(bytes(key, 'utf-8'), ekey):
                print (" *** Keys unpacked to {} directory".format(manager.directory))
            
        else:
            self.__manual()

backup = Backup()
backup.process()
