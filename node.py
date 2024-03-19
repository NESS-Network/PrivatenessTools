import os
import sys

from framework.Container import Container

from NessKeys.exceptions.NodesFileDoesNotExist import NodesFileDoesNotExist
from NessKeys.exceptions.MyNodesFileDoesNotExist import MyNodesFileDoesNotExist
from NessKeys.exceptions.UsersKeyDoesNotExist import UsersKeyDoesNotExist
from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.UserNotFound import UserNotFound
from NessKeys.exceptions.NodeNotSelected import NodeNotSelected
from NessKeys.exceptions.NodeError import NodeError
from NessKeys.exceptions.AuthError import AuthError

import requests
from framework.ARGS import ARGS
from prettytable import PrettyTable

class Noder:

    def __manual(self):
        print("*** Node manipulation")
        print("### USAGE:")
        print("#### List all nodes (previously fetched from blockchain or remote node):")
        print(" python node.py list")
        print("#### Set current node (you will be registered in that node):")
        print(" python node.py sel <node-name>")

    def process(self):
        km = Container.KeyManager()
        nm = Container.NodeManager()
        fm = Container.FileManager()

        if ARGS.args(['list']) or ARGS.args(['ls']):
            t = PrettyTable(['Nodes'])
            t.align = 'c'

            try:
                nodes = nm.listNodes()
                current_node = nm.getCurrentNodeName()

                for node in nodes:
                    mode_url = node['url']
                    if current_node == mode_url:
                        mode_url = '==> ' +mode_url + ' <=='

                    t.add_row([mode_url])

                print(t)

            except NodesFileDoesNotExist as e:
                print("NODES LIST file not found.")
                print("RUN python nodes-update.py node node-url")

        elif ARGS.args(['select', str]) or ARGS.args(['sel', str]) or ARGS.args(['sl', str]):
            try:
                node_url = sys.argv[2]

                fm.join("", node_url)

            except NodesFileDoesNotExist as e:
                print("NODES LIST file not found.")
                print("RUN python nodes-update.py node node-url")
            except UsersKeyDoesNotExist as e:
                print("Users key not found")
                print("RUN user generation (python keygen.py user ......)")
            except NodeNotFound as e:
                print("NODE '{}' is not in nodes list".format(e.node))
            except NodeError as e:
                print("Error on remote node ")
            except AuthError as e:
                print("Responce verification error")

        elif len(sys.argv) == 2 and sys.argv[1].lower() == 'userinfo':
            try:
                userinfo = nm.userinfo()

                t = PrettyTable(['Param', 'value'])
                t.align = 'l'

                t.add_row(["Payment address", userinfo['addr']])
                t.add_row(["User counter", userinfo['counter']])
                t.add_row(["User shadowname", userinfo['shadowname']])
                t.add_row(["Joined to node", userinfo['joined']])
                t.add_row(["Active on node", userinfo['is_active']])

                print(t)

                print(" * Balance:")

                t = PrettyTable(['Param', 'value'])
                t.align = 'l'
                t.add_row(["Coins", userinfo['balance']['coins']])
                t.add_row(["Coin-hours (total)", userinfo['balance']['hours']])
                t.add_row(["Coin-hours (fee)", userinfo['balance']['fee']])
                t.add_row(["Coin-hours (available)", userinfo['balance']['available']])

                print(t)

            except MyNodesFileDoesNotExist as e:
                print("MY NODES file not found.")
                print("RUN python node.py select <node-url>")
            except NodeNotSelected as e:
                print("Node not selected")
                print("RUN python node.py select <node-url>")
            except UserNotFound as e:
                print("User '{}' is not in users list".format(e.username))
            except NodeNotFound as e:
                print("NODE '{}' is not in nodes list".format(e.node))
            except NodeError as e:
                print("Error on remote node ")
            except AuthError as e:
                print("Responce verification error")

        elif len(sys.argv) == 3 and sys.argv[1].lower() == 'info':
            node_url = sys.argv[2]
            node_info = nm.info(node_url)

            t = PrettyTable(['Param', 'value'])
            t.align = 'l'

            if 'files' in node_info:
                t.add_row(["Max Storage", node_info['files']['quota']])

            t.add_row(["Slots", node_info['slots']])
            t.add_row(["Free slots", node_info['slots_free']])

            print( t )

        elif len(sys.argv) == 2 and (sys.argv[1].lower() == 'help' or sys.argv[1].lower() == '-h'):
            self.__manual()

        else:
            self.__manual()

upd = Noder()
upd.process()