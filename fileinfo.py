import os
import sys

from framework.Container import Container

from NessKeys.exceptions.MyNodesFileDoesNotExist import MyNodesFileDoesNotExist
from NessKeys.exceptions.NodesFileDoesNotExist import NodesFileDoesNotExist
from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.NodeError import NodeError
from NessKeys.exceptions.AuthError import AuthError

import requests
from prettytable import PrettyTable

class Noder:

    def __manual(self):
        print("*** File info")
        print("### USAGE:")
        print(" python fileinfo.py <file_shadowname>")

    def process(self):

        if len(sys.argv) == 2 and (sys.argv[1].lower() == 'help' or sys.argv[1].lower() == '-h'):
            self.__manual()

        elif len(sys.argv) == 2:
            file_shadowname = sys.argv[1]

            km = Container.KeyManager()
            ns = Container.NodeService()
            fs = Container.FilesService()
        
            try:
                if ns.joined(km.getCurrentNodeName()):
                    fileinfo = fs.fileinfo(file_shadowname)

                    if fileinfo != False:
                        print(" *** fileinfo *** ")
                        t = PrettyTable(['Param', 'value'])

                        t.add_row(["File ID", fileinfo['id']])
                        t.add_row(["Filename", fileinfo['filename']])
                        t.add_row(["Shadowname", fileinfo['shadowname']])
                        t.add_row(["Status", fileinfo['status']])
                        t.add_row(["Filesize (local)", fileinfo['size_local']])
                        t.add_row(["Filesize (remote)", fileinfo['size_remote']])
                        t.add_row(["Filepath (local)", fileinfo['filepath']])
                        t.add_row(["Cipher", fileinfo['cipher']])
                        t.add_row(["Encryption key", fileinfo['key']])
                        t.add_row(["Public link", fileinfo['pub']])

                        t.align = 'l'
                        print(t)
                    else:
                        print("File {} does not exist".format(file_shadowname))

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

upd = Noder()
upd.process()