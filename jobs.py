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

import requests
import signal

def exit_fn (*args):
    GLOBAL.halt = True

signal.signal(signal.SIGINT, exit_fn)
signal.signal(signal.SIGTERM, exit_fn)

class Jobs:

    def __manual(self):
        print("*** File jobs")
        print("### USAGE:")
        print("#### List jobs")
        print(" ./jobs ls")
        print(" ./jobs list")
        print("#### Pause job")
        print(" ./jobs pause <file shadowname with current running job>")
        print("#### Resume job")
        print(" ./jobs run <file shadowname with current paused job>")

    def process(self):

        if ARGS.args(['help']) or ARGS.args(['-h']):
            self.__manual()

        elif ARGS.args(['ls']) or ARGS.args(['list']):

            fm = Container.FileManager()
            fm.initKeys()
            fm.initKeys()
            
            try:
                fm.jobs()
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

        elif ARGS.args(['pause', str]):
            shadowname = sys.argv[2]

            fm = Container.FileManager()
            fm.initKeys()
            
            try:
                fm.pauseJob(shadowname)
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


        elif ARGS.args(['run', str]):
            shadowname = sys.argv[2]

            fm = Container.FileManager()
            fm.initKeys()
            
            try:
                fm.runJob(shadowname)
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

jbs = Jobs()
jbs.process()