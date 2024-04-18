import os
import sys
from base64 import b64encode
from base64 import b64decode
import uuid

from framework.Container import Container
from framework.GLOBAL import GLOBAL
from framework.ARGS import ARGS

from NessKeys.exceptions.MyNodesFileDoesNotExist import MyNodesFileDoesNotExist
from NessKeys.exceptions.NodesFileDoesNotExist import NodesFileDoesNotExist
from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.FileNotExist import FileNotExist
from NessKeys.exceptions.NodeNotSelected import NodeNotSelected
from NessKeys.exceptions.NodeError import NodeError
from NessKeys.exceptions.AuthError import AuthError

import NessKeys.Prng as prng

import requests
import signal

def exit_fn (*args):
    GLOBAL.halt = True

signal.signal(signal.SIGINT, exit_fn)
signal.signal(signal.SIGTERM, exit_fn)

class Uploader:

    def __manual(self):
        print("*** File upload")
        print("### USAGE:")
        # print("#### Upload file on service node")
        # print(" ./upload <path to your file to upload>")
        print("#### Upload and encrypt file on service node")
        print(" ./upload enc <path to your file to upload>")
        print(" ./upload encrypt <path to your file to upload>")
        print("#### Upload file on service node with filename=shadowname")
        print(" ./upload <path to your file to upload>")
        print(" ./upload pub <path to your file to upload>")
        print(" ./upload public <path to your file to upload>")

    def process(self):

        if ARGS.args(['help']) or ARGS.args(['-h']):
            self.__manual()

        elif ARGS.args(['enc', str]) or ARGS.args(['encrypt', str]):
            filepath = sys.argv[2]

            fm = Container.FileManager()
            
            try:
                fm.UploadEncrypt(filepath)

            except FileNotExist as e:
                print("File '{}' does not exist".format(e.filename))
            except NodeNotSelected as e:
                print("Node '{}' is not joined".format(e.node_url))
                print("RUN ./node sel node-url")
            except MyNodesFileDoesNotExist as e:
                print("MY NODES file not found.")
                print("RUN ./node set node-url")
            except NodesFileDoesNotExist as e:
                print("NODES LIST file not found.")
                print("RUN ./nodes-update node node-url")
            except NodeNotFound as e:
                print("NODE '{}' is not in nodes list".format(e.node))
            except NodeError as e:
                print("Error on remote node: " + e.error)
            except AuthError as e:
                print("Responce verification error")


        elif ARGS.args([str]) or ARGS.args(['pub', str]):
            if len(sys.argv) == 3:
                filepath = sys.argv[2]
            else:
                filepath = sys.argv[1]

            fm = Container.FileManager()
            fm.initKeys()
            
            try:
                fm.upload(filepath)
                fm.saveKeys()

            except FileNotExist as e:
                print("File '{}' does not exist".format(e.filename))
            except NodeNotSelected as e:
                print("Node '{}' is not joined".format(e.node_url))
                print("RUN ./node sel node-url")
            except MyNodesFileDoesNotExist as e:
                print("MY NODES file not found.")
                print("RUN ./node set node-url")
            except NodesFileDoesNotExist as e:
                print("NODES LIST file not found.")
                print("RUN ./nodes-update node node-url")
            except NodeNotFound as e:
                print("NODE '{}' is not in nodes list".format(e.node))
            except NodeError as e:
                print("Error on remote node: " + e.error)
            except AuthError as e:
                print("Responce verification error")
        else:
            self.__manual()

upd = Uploader()
upd.process()