import os
import sys

from framework.Container import Container

from NessKeys.exceptions.MyNodesFileDoesNotExist import MyNodesFileDoesNotExist
from NessKeys.exceptions.NodesFileDoesNotExist import NodesFileDoesNotExist
from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.NodeError import NodeError
from NessKeys.exceptions.AuthError import AuthError
from NessKeys.exceptions.FileNotExist import FileNotExist

import requests
from prettytable import PrettyTable

class DIR:

    def __manual(self):
        print("*** Move to other directory")
        print("### USAGE:")
        print(" ./move <File shadowname or Directory ID> <Directory ID>")

    def process(self):

        if len(sys.argv) == 2 and (sys.argv[1].lower() == 'help' or sys.argv[1].lower() == '-h'):
            self.__manual()

        elif len(sys.argv) == 3:
            fm = Container.FileManager()
            km = Container.KeyManager()
            fm.initKeys()

            try:
                ID = sys.argv[1]
                parent_id = int(sys.argv[2])

                fm.move(ID, parent_id)

                if km.isFile(ID):
                    name = ID
                else:
                    dir = km.getDirectory(int(ID))
                    name = dir['name']

                dir = km.getDirectory(parent_id)
                print(' *** {} moved to {}'.format(name, dir['name']))

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
            except FileNotExist as e:
                print("File {} does not exist".format(e.filename))

        else:
            self.__manual()

upd = DIR()
upd.process()