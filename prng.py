import os
import sys

from framework.Container import Container
from framework.ARGS import ARGS
import NessKeys.Prng as prng
from ness.NessAuth import NessAuth

from NessKeys.exceptions.MyNodesFileDoesNotExist import MyNodesFileDoesNotExist
from NessKeys.exceptions.NodesFileDoesNotExist import NodesFileDoesNotExist
from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.NodeError import NodeError
from NessKeys.exceptions.AuthError import AuthError
from NessKeys.exceptions.NodeNotSelected import NodeNotSelected

import requests

class Lister:

    def __manual(self):
        print("*** Show random data")
        print("### USAGE:")
        print("#### Show random generated seed:")
        print(" ./prng seed")
        print("#### Show random generated seed (big):")
        print(" ./prng seedb")
        print("#### Show random generated numbers:")
        print(" ./prng numbers")
        print("#### Show random generated numbers (many):")
        print(" ./prng numbersb")
        print("#### Show random generated 256 bit number (int, ethereum):")
        print(" ./prng i256")
        print("#### Show random generated 256 bit number (hex, ethereum):")
        print(" ./prng h256")

    def nodefn(self, fn: str):
        km = Container.KeyManager()
        auth = NessAuth()

        my = km.getMyNodesKey()
        node_url = my.getCurrentNodeUrl()
        url = node_url + "/prng/" + fn
        username = my.getCurrentNodeUsername()

        Users = km.getUsersKey()
        Nodes = km.getNodesKey()

        if Users.findUser(username) == False:
            raise UserNotFound(username)

        user_private_key = Users.getPrivateKey(username)
        user_nonce = Users.getNonce(username)
        node = Nodes.findNode(node_url)

        if node == False:
            raise NodeNotFound(node_url)

        node_nonce = node['nonce']
        node_verify = node['verify']
        node_public = node['public']

        result = auth.get_by_auth_id(url, user_private_key, node_url, node_nonce, username, username, user_nonce)

        if result['result'] == 'error':
            raise NodeError(result['error'])

        print (result['data'][fn])

    def process(self):
        try:
            if ARGS.args(['seed']):
                self.nodefn('seed')
            elif ARGS.args(['seedb']):
                self.nodefn('seedb')
            elif ARGS.args(['numbers']):
                self.nodefn('numbers')
            elif ARGS.args(['numbersb']):
                self.nodefn('numbersb')
            elif ARGS.args(['i256']):
                self.nodefn('i256')
            elif ARGS.args(['h256']):
                self.nodefn('h256')
            else:
                self.__manual()
                
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

ls = Lister()
ls.process()