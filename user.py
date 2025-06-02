import os
import sys

from framework.Container import Container

from NessKeys.exceptions.MyNodesFileDoesNotExist import MyNodesFileDoesNotExist
from NessKeys.exceptions.NodesFileDoesNotExist import NodesFileDoesNotExist
from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.NodeError import NodeError
from NessKeys.exceptions.AuthError import AuthError

from prettytable import PrettyTable
import humanize
from framework.ARGS import ARGS

class Noder:

    def __manual(self):
        print("*** User list and user selection")
        print("### USAGE:")
        print("#### Show current user and current node")
        print(" ./user")
        print("#### Show userlist")
        print(" ./user list|ls")
        print("#### Select user")
        print(" ./user sel|sl username")
        print("#### Check if current user is registered in blockchain")
        print(" ./user check|chk|ch")
        print("#### Show current user nvs")
        print(" ./user nvs")
        print("#### Show current user <WORM>")
        print(" ./user worm")
        print("#### Edit users file")
        print(" ./user edit [editor=nano]")

    def __userinfo(self):
        km = Container.KeyManager()
        current_node = km.getCurrentNodeName()
        current_user = km.getCurrentUser()

        if current_node == False:
            current_node = "[NOT SELECTED]"

        if current_user == False:
            current_user = "[NOT SELECTED]"

        print(" *** {} at {}".format(current_user, current_node))

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
        if ARGS.args(['list']) or ARGS.args(['ls']):
            self.print_userlist()

        elif ARGS.args(['edit']):
            os.system("nano ~/.privateness-keys/users.key.json") 

        elif ARGS.args(['edit', str]):
            os.system(ARGS.arg(2) + " ~/.privateness-keys/users.key.json") 

        elif ARGS.args(['nvs']):
            manager = Container.KeyManager()
            users_key = manager.showUsersKey()
            print(users_key['nvs'])

        elif ARGS.args(['worm']):
            manager = Container.KeyManager()
            users_key = manager.showUsersKey()
            print(users_key['worm'])

        elif ARGS.args(['sel', str]) or ARGS.args(['sl', str]):
            manager = Container.KeyManager()

            try:
                manager.changeCurrentUser(sys.argv[2])            
            except NodeNotSelected as e:
                print("No node selected")
                print("Run $ ./node sel <node_url>")

            self.print_userlist()

        elif ARGS.args(['check']) or ARGS.args(['chk']) or ARGS.args(['ch']):
            manager = Container.KeyManager()
            username = manager.getCurrentUser()
            node = manager.getRandomNode()

            if node:
                node_url = node['url']
                ns = Container.NodeService()

                if ns.exist(node_url, username):
                    print ("User '{}' REGISTERED in blockchain".format(username))
                else:
                    print ("User '{}' is NOT registered in blockchain".format(username))
            else:
                print("NODES LIST file not found.")
                print("RUN ./nodes-update node node-url")

        elif len(sys.argv) == 2 and (sys.argv[1].lower() == 'help' or sys.argv[1].lower() == '-h'):
            self.__manual()

        else:
            self.__userinfo()

upd = Noder()
upd.process()