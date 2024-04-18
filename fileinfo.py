import os
import sys

from framework.Container import Container

from NessKeys.exceptions.MyNodesFileDoesNotExist import MyNodesFileDoesNotExist
from NessKeys.exceptions.NodesFileDoesNotExist import NodesFileDoesNotExist
from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.FileNotExist import FileNotExist
from NessKeys.exceptions.NodeError import NodeError
from NessKeys.exceptions.AuthError import AuthError

import requests
from prettytable import PrettyTable

class Noder:

    def __manual(self):
        print("*** File info")
        print("### USAGE:")
        print(" ./fileinfo <file_shadowname>")

    def process(self):

        if len(sys.argv) == 2 and (sys.argv[1].lower() == 'help' or sys.argv[1].lower() == '-h'):
            self.__manual()

        elif len(sys.argv) == 2:
            file_shadowname = sys.argv[1]

            fm = Container.FileManager()
            fm.initKeys()
        
            try:
                fm.fileinfo(file_shadowname)
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

        else:
            self.__manual()

upd = Noder()
upd.process()