import os
import sys

from framework.Container import Container

from NessKeys.exceptions.MyNodesFileDoesNotExist import MyNodesFileDoesNotExist
from NessKeys.exceptions.NodesFileDoesNotExist import NodesFileDoesNotExist
from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.NodeError import NodeError
from NessKeys.exceptions.AuthError import AuthError
from NessKeys.exceptions.NodeNotSelected import NodeNotSelected
from NessKeys.exceptions.DirectoryNotEmpty import DirectoryNotEmpty
from NessKeys.exceptions.DirNotExist import DirNotExist

import requests
from prettytable import PrettyTable

class DIR:

    def __manual(self):
        print("*** File info")
        print("### USAGE:")
        print(" ./rmdir <Directory ID>")

    def process(self):

        if len(sys.argv) == 2 and (sys.argv[1].lower() == 'help' or sys.argv[1].lower() == '-h'):
            self.__manual()

        elif len(sys.argv) == 2:
            directory_id = int(sys.argv[1])

            fm = Container.FileManager()
            km = Container.KeyManager()
            fm.initKeys()

            try:
                dir = km.getDirectory(directory_id)
                fm.rmdir(directory_id)
                fm.saveKeys()

                print ("Directory {} removed".format(dir['name']))

            except DirNotExist as e:
                print("Directory {} does not exist".format(e.id))
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
            except NodeNotSelected as e:
                print("Current node is not set or not joined, try: ./node sel <node_url>")

        else:
            self.__manual()

upd = DIR()
upd.process()