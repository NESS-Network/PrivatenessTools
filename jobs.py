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
        print(" python jobs.py ls")
        print(" python jobs.py list")
        print("#### Pause job")
        print(" python jobs.py pause <file shadowname with current running job>")
        print("#### Resume job")
        print(" python jobs.py run <file shadowname with current paused job>")

    def process(self):

        if ARGS.args(['help']) or ARGS.args(['-h']):
            self.__manual()

        elif ARGS.args(['ls']) or ARGS.args(['list']):

            fm = Container.FileManager()
            
            try:
                fm.jobs()

            except FileNotExist as e:
                print("File '{}' does not exist".format(e.filename))
            except NodeNotSelected as e:
                print("Node '{}' is not joined".format(e.node_url))
                print("RUN python node.py sel node-url")
            except MyNodesFileDoesNotExist as e:
                print("MY NODES file not found.")
                print("RUN python node.py set node-url")
            except NodesFileDoesNotExist as e:
                print("NODES LIST file not found.")
                print("RUN python nodes-update.py node node-url")
            except NodeNotFound as e:
                print("NODE '{}' is not in nodes list".format(e.node))
            except NodeError as e:
                print("Error on remote node: " + e.error)
            except AuthError as e:
                print("Responce verification error")

        elif ARGS.args(['pause', str]):
            shadowname = sys.argv[2]

            fm = Container.FileManager()
            
            try:
                fm.pauseJob(shadowname)

            except FileNotExist as e:
                print("File '{}' does not exist".format(e.filename))
            except NodeNotSelected as e:
                print("Node '{}' is not joined".format(e.node_url))
                print("RUN python node.py sel node-url")
            except MyNodesFileDoesNotExist as e:
                print("MY NODES file not found.")
                print("RUN python node.py set node-url")
            except NodesFileDoesNotExist as e:
                print("NODES LIST file not found.")
                print("RUN python nodes-update.py node node-url")
            except NodeNotFound as e:
                print("NODE '{}' is not in nodes list".format(e.node))
            except NodeError as e:
                print("Error on remote node: " + e.error)
            except AuthError as e:
                print("Responce verification error")


        elif ARGS.args(['run', str]):
            shadowname = sys.argv[2]

            fm = Container.FileManager()
            
            try:
                fm.runJob(shadowname)

            except FileNotExist as e:
                print("File '{}' does not exist".format(e.filename))
            except NodeNotSelected as e:
                print("Node '{}' is not joined".format(e.node_url))
                print("RUN python node.py sel node-url")
            except MyNodesFileDoesNotExist as e:
                print("MY NODES file not found.")
                print("RUN python node.py set node-url")
            except NodesFileDoesNotExist as e:
                print("NODES LIST file not found.")
                print("RUN python nodes-update.py node node-url")
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