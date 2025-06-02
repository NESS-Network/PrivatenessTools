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
        print("*** Human list and human selection")
        print("### USAGE:")
        print("#### Show human list")
        print(" ./human list|ls")
        print("#### Select human")
        print(" ./human sel|sl humanname")
        print("#### Check if current human is registered in blockchain")
        print(" ./human check|chk|ch")
        print("#### Sign other key with human")
        print(" ./human sign")
        print("#### Show current human nvs")
        print(" ./human nvs")
        print("#### Show current human <WORM>")
        print(" ./human worm")
        print("#### Edit humans file")
        print(" ./human edit [editor=nano]")


    def print_humanlist(self):
        manager = Container.KeyManager()
        humans_key = manager.showHumansKey()

        t = PrettyTable(['Human'])
        t.align = 'c'
        
        if humans_key != False:
            for human in humans_key['humans']:
                if human == humans_key['current']:
                    humanname = '==> ' + human + ' <=='
                else:
                    humanname = human

                t.add_row([humanname])

        t.align = 'c'
        print(t)

    def process(self):
        if ARGS.args(['list']) or ARGS.args(['ls']):
            self.print_humanlist()

        elif ARGS.args(['edit']):
            os.system("nano ~/.privateness-keys/humans.key.json") 

        elif ARGS.args(['edit', str]):
            os.system(ARGS.arg(2) + " ~/.privateness-keys/humans.key.json") 

        elif ARGS.args(['nvs']):
            manager = Container.KeyManager()
            humans_key = manager.showHumansKey()
            print(humans_key['nvs'])

        elif ARGS.args(['worm']):
            manager = Container.KeyManager()
            humans_key = manager.showHumansKey()
            print(humans_key['worm'])

        elif ARGS.args(['sel', str]) or ARGS.args(['sl', str]):
            manager = Container.KeyManager()
            manager.changeCurrentHuman(sys.argv[2])
            self.print_humanlist()

        elif ARGS.args(['check']) or ARGS.args(['chk']) or ARGS.args(['ch']):
            manager = Container.KeyManager()
            humanname = manager.getCurrentHuman()
            node = manager.getRandomNode()

            if node:
                node_url = node['url']
                ns = Container.NodeService()

                if ns.exist(node_url, humanname):
                    print ("Human '{}' REGISTERED in blockchain".format(humanname))
                else:
                    print ("Human '{}' is NOT registered in blockchain".format(humanname))
            else:
                print("NODES LIST file not found.")
                print("RUN ./nodes-update node node-url")

        elif len(sys.argv) == 2 and (sys.argv[1].lower() == 'help' or sys.argv[1].lower() == '-h'):
            self.__manual()

        else:
            self.__manual()

upd = Noder()
upd.process()