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
import humanize

class Noder:

    def __manual(self):
        print("*** User list and user selection")
        print("### USAGE:")
        print("#### Show userlist")
        print(" python users.py")
        print("#### Show current user nvs")
        print(" python users.py nvs")
        print("#### Show current user <WORM>")
        print(" python users.py worm")
        print("#### Select new user")
        print(" python users.py <username>")

    def print_userlist(self):
        manager = Container.KeyManager()
        users_key = manager.showUsersKey()

        t = PrettyTable(['Username'])
        t.align = 'c'
        
        if users_key != False:
            for user in users_key['users']:
                if user == users_key['current']:
                    username = '==> ' + user + ' <=='
                else:
                    username = user

                t.add_row([username])

        t.align = 'c'
        print(t)

    def process(self):

        if len(sys.argv) == 1:
            self.print_userlist()

        elif len(sys.argv) == 2 and sys.argv[1].lower() == 'nvs':
            manager = Container.KeyManager()
            users_key = manager.showUsersKey()
            print(users_key['nvs'])

        elif len(sys.argv) == 2 and sys.argv[1].lower() == 'worm':
            manager = Container.KeyManager()
            users_key = manager.showUsersKey()
            print(users_key['worm'])

        elif len(sys.argv) == 2 and sys.argv[1].lower() == 'info':
            km = Container.KeyManager()
            ns = Container.NodeService()
            
            try:
                print(" # Current node: " + km.getCurrentNodeName())
                userinfo = ns.userinfo()

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
                print("RUN python node.py set node-url")
            except NodesFileDoesNotExist as e:
                print("NODES LIST file not found.")
                print("RUN python nodes-update.py node node-url")
            except NodeNotFound as e:
                print("NODE '{}' is not in nodes list".format(e.node))
            except NodeError as e:
                print("Error on remote node ")
            except AuthError as e:
                print("Responce verification error")

        elif len(sys.argv) == 2 and sys.argv[1].lower() == 'out':
            pass

        elif len(sys.argv) == 3 and sys.argv[1].lower() == 'sel':
            manager = Container.KeyManager()
            manager.changeCurrentUser(sys.argv[2])
            self.print_userlist()

        elif len(sys.argv) == 2 and (sys.argv[1].lower() == 'help' or sys.argv[1].lower() == '-h'):
            self.__manual()

upd = Noder()
upd.process()