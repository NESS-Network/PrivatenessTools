import os
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

import uuid
import NessKeys.Prng as prng
from framework.Container import Container
from NessKeys.cryptors.Salsa20 import Salsa20

from NessKeys.exceptions.KeyIndexException import KeyIndexException
from NessKeys.JsonChecker.exceptions.LeafBuildException import LeafBuildException
from NessKeys.exceptions.CrcCheck import CrcCheck

import getpass

class Key:

    def __manual(self):
        print("*** PrivateNess KEY UTILITY")
        print("### DESCRIPTION:")
        print("  Privateness keys infrastructure management")
        print("### USAGE:")
        print("### List Keys")
        print("#### Show all contents of keyfile")
        print("./key list [dirpath]")
        print("### Show Key")
        print("#### Show all contents of keyfile")
        print("./key show <keyfile>")
        print("#### show nvs name (for blockchain)")
        print("./key nvs <keyfile>")
        print("#### Show <worm> for blockchain (if there are any)")
        print("./key worm <keyfile>")
        print("#### Show all encrypted keys (if there are any)")
        print("./key list <keyfile>")
        print("### Pack keyfiles into encrypted keyfile")
        print("./key pack <keyfile1,keyfile2, ...> <encrypted keyfile>")
        print("### Unpack keyfiles from encrypted keyfile")
        print("./key unpack <encrypted keyfile>")
        print("### Save local keyfiles into encrypted keyfile")
        print("./key save <encrypted keyfile>")
        print("### Restore local keyfiles from encrypted keyfile")
        print("./key restore <encrypted keyfile>")
        print("### Eraise keyfile or all local keyfiles (fill with 0)")
        print("./key eraise [encrypted keyfile]")

        km = Container.KeyManager()
        print("\nKeys directory: " + km.directory)

    def process(self):
        if len(sys.argv) == 3 and sys.argv[1].lower() == 'show':
            filename = sys.argv[2]
            try:
                km = Container.KeyManager()
                print(km.showKey(filename))
            except json.decoder.JSONDecodeError as e:
                print("File format error")
            except LeafBuildException as e:
                print("File format error: \"{}\" path: {}".format(e.msg, e.path))

        elif len(sys.argv) == 3 and sys.argv[1].lower() == 'nvs':
            filename = sys.argv[2]
            try:
                km = Container.KeyManager()
                print(km.showKeyNVS(filename))
            except json.decoder.JSONDecodeError as e:
                print("File format error")
            except LeafBuildException as e:
                print("File format error: \"{}\" path: {}".format(e.msg, e.path))

        elif len(sys.argv) == 3 and sys.argv[1].lower() == 'worm':
            filename = sys.argv[2]
            try:
                km = Container.KeyManager()
                print(km.showKeyWorm(filename))
            except json.decoder.JSONDecodeError as e:
                print("File format error")
            except LeafBuildException as e:
                print("File format error: \"{}\" path: {}".format(e.msg, e.path))

        elif len(sys.argv) == 2 and sys.argv[1].lower() == 'list':
            km = Container.KeyManager()
            files = glob.glob('*.key.json')
            
            for filename in files:
                print(" *** {}".format(filename))
                try:
                    print(km.showKey(filename))
                except json.decoder.JSONDecodeError as e:
                    print("File format error")
                except LeafBuildException as e:
                    print("File format error: \"{}\" path: {}".format(e.msg, e.path))

        elif len(sys.argv) == 3 and sys.argv[1].lower() == 'list':
            file_arg = sys.argv[2]

            if os.path.exists(file_arg): 
                if os.path.isfile(file_arg):
                    # Packed file listing
                    km = Container.KeyManager()

                    password = getpass.getpass("Type password:")

                    try:
                        km.listKeys(file_arg, password)
                    except LeafBuildException as e:
                        print("File format error: \"{}\" path: {}".format(e.msg, e.path))
                    except CrcCheck as e:
                        print("Wrong password (CRC check error)")
                else:
                    # Directory listing

                    km = Container.KeyManager()
                    path = file_arg + '/*.key.json'
                    files = glob.glob(path)
                    
                    for filename in files:
                        print(" *** {}".format(filename))
                        try:
                            print(km.showKey(filename))
                        except json.decoder.JSONDecodeError as e:
                            print("File format error")
                        except LeafBuildException as e:
                            print("File format error: \"{}\" path: {}".format(e.msg, e.path))

        elif len(sys.argv) == 4 and sys.argv[1].lower() == 'pack':
            km = Container.KeyManager()
            packet_keyfile = sys.argv[3]
            keys = sys.argv[2]

            password = getpass.getpass("Type password:")
            password2 = getpass.getpass("Confirm password:")

            if password != password2:
                print("Passwords does not match")
                return False

            try:
                km.packKeysPassword(keys.split(','), packet_keyfile, password)
            except LeafBuildException as e:
                print("File format error: \"{}\" path: {}".format(e.msg, e.path))

        elif len(sys.argv) == 3 and sys.argv[1].lower() == 'unpack':
            km = Container.KeyManager()

            password = getpass.getpass("Type password:")

            try:
                km.unpackKeysPassword(sys.argv[2], password)
            except LeafBuildException as e:
                print("File format error: \"{}\" path: {}".format(e.msg, e.path))
            except CrcCheck as e:
                print("Wrong password (CRC check error)")

        # elif len(sys.argv) == 3 and sys.argv[1].lower() == 'init':
        #     km = Container.KeyManager()
        #     user_keyfile = sys.argv[2]

        #     km.init(user_keyfile)

        # elif len(sys.argv) == 3 and sys.argv[1].lower() == 'node':
        #     km = Container.KeyManager()
        #     node_keyfile = sys.argv[2]

        #     km.init_node(node_keyfile)

        elif len(sys.argv) == 2 and sys.argv[1].lower() == 'eraise':
            answer = input("Eraise all local keys y/n :")
            if answer.lower() == 'y':
                km = Container.KeyManager()
                km.eraiseAll()

            print("Keyfiles eraised !")

        elif len(sys.argv) == 3 and sys.argv[1].lower() == 'eraise':
            km = Container.KeyManager()
            keyfile = sys.argv[2]

            if os.path.exists(keyfile):
                answer = input("Eraise all local keys y/n :")
                if answer.lower() == 'y':
                    km.eraise(keyfile)
                    print ("File '%s' eraised" % (keyfile))
            else:
                print ("File '%s' does not exist" % (keyfile))

        elif len(sys.argv) == 3 and sys.argv[1].lower() == 'save':
            km = Container.KeyManager()
            keyfile = sys.argv[2]

            password = getpass.getpass("Type password:")
            password2 = getpass.getpass("Confirm password:")

            if password != password2:
                print("Passwords does not match")
                return False

            km.save(keyfile, password)

            print("Keyfiles saved !")

        elif len(sys.argv) == 3 and sys.argv[1].lower() == 'restore':
            keyfile = sys.argv[2]
            km = Container.KeyManager()

            password = getpass.getpass("Type password:")      

            try:
                km.restore(keyfile, password)
            except LeafBuildException as e:
                print("File format error: \"{}\" path: {}".format(e.msg, e.path))
            except CrcCheck as e:
                print("Wrong password (CRC check error)")

            print("Keyfiles restored !")

        else:
            self.__manual()

kkk = Key()
kkk.process()