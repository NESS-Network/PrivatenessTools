import os
import sys

from framework.Container import Container

from NessKeys.exceptions.MyNodesFileDoesNotExist import MyNodesFileDoesNotExist
from NessKeys.exceptions.NodesFileDoesNotExist import NodesFileDoesNotExist
from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.NodeError import NodeError
from NessKeys.exceptions.AuthError import AuthError

import requests

class Lister:

    def __manual(self):
        print("*** Directory tree")
        print("### USAGE:")
        print("#### List directories only")
        print(" ./tree")
        print("#### List directories with files")
        print(" ./tree files")

    def process(self):

        if len(sys.argv) == 1:
            fm = Container.FileManager()
            km = Container.KeyManager()
            fm.initKeys()

            try:
                tree = fm.tree()
                current_dir = km.getCurrentDir()

                def print_dir(dirs : dict, level: int):
                    for id in dirs:
                        files = km.getFiles(int(id))
                        name = id + ': [' + dirs[id]['name'] + ']'

                        if len(files) > 0:
                            name += '({})'.format(len(files))

                        if int(id) == current_dir:
                            name = '==> ' + name + ' <=='
                            line = " " * level * 4 + name
                        else:
                            line = " " * (level + 1) * 4 + name

                        print(line)

                        if 'children' in dirs[id]:
                            print_dir(dirs[id]['children'], level + 1)

                print_dir(tree, 0)
                fm.saveKeys()

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

        elif len(sys.argv) == 2 and sys.argv[1].lower() == 'files':
            fm = Container.FileManager()
            km = Container.KeyManager()
            fm.initKeys()
            
            try:
                tree = fm.tree()
                current_dir = km.getCurrentDir()

                def print_dir(dirs : dict, level: int):
                    for id in dirs:
                        files = km.getFiles(int(id))
                        name = id + ': [' + dirs[id]['name'] + ']'

                        if int(id) == current_dir:
                            name = '==> ' + name + ' <=='
                            line = " " * level * 4 + name
                        else:
                            line = " " * (level + 1) * 4 + name

                        print(line)

                        if 'children' in dirs[id]:
                            print_dir(dirs[id]['children'], level + 1)

                        if len(files) > 0:
                            for  sh in files:
                                fline = "{}: {}".format(sh, files[sh]['filename'])
                                fline = " " * (level + 2) * 4 + fline
                                print(fline)

                print_dir(tree, 0)
                fm.saveKeys()

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

ls = Lister()
ls.process()