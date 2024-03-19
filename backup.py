import os
import sys
from base64 import b64encode
from base64 import b64decode
import json
import urllib.parse
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import datetime

import uuid
import NessKeys.Prng as prng
from framework.Container import Container
from framework.ARGS import ARGS

class Backup:

    def __manual(self):
        print("*** PrivateNess keys BACKUP")
        print("### Show backup SEED")
        print(" python backup.py seed")
        print("### Show backup ADDRESS")
        print(" python backup.py address")
        print("### Do backup to selected NODE or to FILE")
        print(" python backup.py backup [filename]")
        print("### Restore backup from current NODE or from FILE")
        print(" python backup.py restore [filename]")

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
            manager = Container.KeyManager()
            bkey = manager.getBackupKey()

            dt = datetime.datetime.now()
            time = dt.strftime("%Y-%m-%d %H:%M:%S")
            filename = "Backup " + time +".json"

            manager.packKeys(manager.getLocalKeyFiles(), bkey.getCipher(), bkey.getKey(), filename)

            if bkey.getType() == 'node':
                pass
                # TODO: Upload file to Selected Node and selected User
                # TODO: Save link to address field

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
            bkey = manager.getBackupKey()

            if bkey == False:
                print ("Backup file not found")
                return False
            
            address = bkey.getAddress(0)
            seed = bkey.getSeed()

            # TODO: Upload file from address
            # TODO: Restore key from seed
            # TODO: unpack file to keys directory
            
        else:
            self.__manual()

backup = Backup()
backup.process()
