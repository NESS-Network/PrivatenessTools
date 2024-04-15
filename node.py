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
        print(" python node.py list all")
        print(" python node.py ls all")
        print("#### List all active nodes:")
        print(" python node.py <list or ls> network service <+-s or +-t or +-q>")
        print("  network: inet yggdrasil tor i2p")
        print("  service: files or prng")
        print("  sorting:")
        print("   +-s free slots")
        print("   +-t tariff (coin hours)")
        print("   +-q file storage quota")
        print("   + ascending order")
        print("   - descending order")
        print("#### Set current node (you will be registered in that node):")
        print(" python node.py sel <node-name>")
        print("#### Show about page")
        print(" python node.py about <node-name>")
        print("#### Show info about node")
        print(" python node.py info <node-name>")
        print("#### Show information about user on selected node")
        print(" python node.py userinfo")

    def process(self):
        km = Container.KeyManager()
        nm = Container.NodeManager()
        fm = Container.FileManager()

        if ARGS.args(['list', 'all']) or ARGS.args(['ls', 'all']):
            print(" *** Nodes")

            t = PrettyTable(['URL', 'Network', 'Services','Tariff'])
            t.align = 'c'

            try:
                nodes = nm.listNodes()
                current_node = nm.getCurrentNodeName()

                for node in nodes:
                    node_url = node['url']
                    if current_node == node_url:
                        node_url = '==> ' +node_url + ' <=='

                    t.add_row([node_url, node['network'], ','.join(node['services']), node['tariff']])

                print(t)

            except NodesFileDoesNotExist as e:
                print("NODES LIST file not found.")
                print("RUN python nodes-update.py node node-url")

            print( type('') == str, type(0) == int )

            exit(0)

        if ARGS.args(['list']) or ARGS.args(['list', str]) or ARGS.args(['list', str, str]) or ARGS.args(['list', str, str, str]) or ARGS.args(['ls']) or ARGS.args(['ls', str]) or ARGS.args(['ls', str, str]) or ARGS.args(['ls', str, str, str]):

            t = PrettyTable(['URL', 'Network', 'Services', 'Tariff', 'Slots (free)', 'Storage quota'])
            t.align = 'c'

            try:
                if len(sys.argv) == 3:
                    nodes = nm.listNodesFull(network = sys.argv[2].lower())
                elif len(sys.argv) == 4:
                    nodes = nm.listNodesFull(network = sys.argv[2].lower(), service=sys.argv[3].lower())
                elif len(sys.argv) == 5:
                    if sys.argv[4] == '+s':
                        nodes = nm.listNodesFull(network = sys.argv[2].lower(), service=sys.argv[3].lower(), sort='slots_free')
                    elif sys.argv[4] == '-s':
                        nodes = nm.listNodesFull(network = sys.argv[2].lower(), service=sys.argv[3].lower(), sort='slots_free', reverse_sort=True)
                    elif sys.argv[4] == '+t':
                        nodes = nm.listNodesFull(network = sys.argv[2].lower(), service=sys.argv[3].lower(), sort='tariff')
                    elif sys.argv[4] == '-t':
                        nodes = nm.listNodesFull(network = sys.argv[2].lower(), service=sys.argv[3].lower(), sort='tariff', reverse_sort=True)
                    elif sys.argv[4] == '+q':
                        nodes = nm.listNodesFull(network = sys.argv[2].lower(), service=sys.argv[3].lower(), sort='quota')
                    elif sys.argv[4] == '-q':
                        nodes = nm.listNodesFull(network = sys.argv[2].lower(), service=sys.argv[3].lower(), sort='quota', reverse_sort=True)
                    else:
                        nodes = nm.listNodesFull()
                else:
                    nodes = nm.listNodesFull(network = sys.argv[2].lower(), service=sys.argv[3].lower())

                for node in nodes:
                    t.add_row([node['caption'], node['network'], node['services'], node['tariff'], node['slots'], node['quota']])

                if len(nodes):
                    print(" *** Nodes")
                    print(t)
                else:
                    print(" *** Nothing found ***")

            except NodesFileDoesNotExist as e:
                print("NODES LIST file not found.")
                print("RUN python nodes-update.py node node-url")

        elif ARGS.args(['select', str]) or ARGS.args(['sel', str]) or ARGS.args(['sl', str]):
            try:
                node_url = sys.argv[2]

                if not nm.nodePing(node_url):
                    print("Node {} is not responding".format(node_url))
                    exit(1)

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

        elif ARGS.args(['about', str]):
            try:
                node_url = sys.argv[2]

                print( nm.about(node_url) )

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
                info = nm.userinfo()
                userinfo = info['userinfo']
                nodeinfo = info['nodeinfo']

                print(" * Nodeinfo:")

                t = PrettyTable(['Param', 'value'])
                t.align = 'l'
                t.add_row(["Network", nodeinfo['network']])
                t.add_row(["Services", ','.join(nodeinfo['services'])])
                t.add_row(["Period (minutes)", nodeinfo['period']])
                t.add_row(["Tariff", nodeinfo['tariff']])

                print(t)

                print(" * Userinfo:")

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

            t.add_row(["Network", node_info['network']])
            t.add_row(["Services", ','.join(node_info['services'])])
            t.add_row(["Slots", node_info['slots']])
            t.add_row(["Free slots", node_info['slots_free']])

            print( t )

        elif len(sys.argv) == 2 and (sys.argv[1].lower() == 'help' or sys.argv[1].lower() == '-h'):
            self.__manual()

        else:
            self.__manual()

upd = Noder()
upd.process()