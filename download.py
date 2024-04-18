import os
import sys

from framework.Container import Container
from framework.GLOBAL import GLOBAL
from framework.ARGS import ARGS

from NessKeys.exceptions.MyNodesFileDoesNotExist import MyNodesFileDoesNotExist
from NessKeys.exceptions.NodesFileDoesNotExist import NodesFileDoesNotExist
from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.FileNotExist import FileNotExist
from NessKeys.exceptions.NodeError import NodeError
from NessKeys.exceptions.AuthError import AuthError
from NessKeys.exceptions.NodeNotSelected import NodeNotSelected

import requests
import signal

def exit_fn (*args):
    GLOBAL.halt = True

signal.signal(signal.SIGINT, exit_fn)
signal.signal(signal.SIGTERM, exit_fn)

class Noder:

    def __manual(self):
        print("*** File download")
        print("### USAGE:")
        print("#### Download file from service node")
        print(" ./download <file_shadowname> [path]")

    def process(self):

        if ARGS.args(['help']) or ARGS.args(['-h']):
            self.__manual()

        elif ARGS.args([str]) or ARGS.args([str, str]):
            shadowname = sys.argv[1]

            if ARGS.args([str, str]):
                path = sys.argv[2]
            else:
                path = ""

            fm = Container.FileManager()
            
            try:
                fm.initKeys()
                fm.download(shadowname, path)
                fm.saveKeys()

            except MyNodesFileDoesNotExist as e:
                print("MY NODES file not found.")
                print("RUN ./node set node-url")
            except NodesFileDoesNotExist as e:
                print("NODES LIST file not found.")
                print("RUN ./nodes-update node node-url")
            except NodeNotFound as e:
                print("NODE '{}' is not in nodes list".format(e.node))
            except FileNotExist as e:
                print("File {} not found".format(e.filename))
            except NodeError as e:
                print("Error on remote node: " + e.error)
            except AuthError as e:
                print("Responce verification error")
            except NodeNotSelected as e:
                print("Current node is not set or not joined, try: ./node sel <node_url>")
        else:
            self.__manual()

upd = Noder()
upd.process()