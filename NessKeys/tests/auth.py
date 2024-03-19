from NessKeys.KeyManager import KeyManager
from NessKeys.StorageJson import StorageJson
from NessKeys.KeyMakerNess import KeyMakerNess
from NessKeys.keys.MyNodes import MyNodes
from NessKeys.keys.Nodes import Nodes
from NessKeys.keys.Users import Users

from NessKeys.exceptions.NodeNotFound import NodeNotFound
from NessKeys.exceptions.NodeError import NodeError
from NessKeys.exceptions.AuthError import AuthError
from NessKeys.exceptions.UserNotFound import UserNotFound

import json
from ness.NessAuth import NessAuth
import math
import os
import requests

from framework.ARGS import ARGS

class AuthTester:

    data_user = {}
    data_node = {}

    def __init__(self):
        storage = StorageJson()
        maker = KeyMakerNess()

        self.km = KeyManager(storage, maker)

        self.Users = self.km.getUsersKey()
        self.Nodes = self.km.getNodesKey()

        self.ness_auth = NessAuth()

    def test(self, username: str, node_url: str):
        url = node_url + "/node/test/auth"

        if self.Users.findUser(username) == False:
            raise UserNotFound(username)

        user_private_key = self.Users.getPrivateKey(username)
        user_nonce = self.Users.getNonce(username)
        node = self.Nodes.findNode(node_url)

        if node == False:
            raise NodeNotFound(node_url)

        node_nonce = node['nonce']
        node_verify = node['verify']
        node_public = node['public']
        result = self.ness_auth.get_by_auth_id(url, user_private_key, node_url, node_nonce, username, username, user_nonce)

        if result['result'] == 'error':
            print(" ~~~ TEST #1 Auth ID FAILED ~~~ ")
            print(result['error'])
        else:
            print(" *** TEST #1 Auth ID OK !!! *** ")
            print(result['message'])

        test_string = 'The state calls its own violence law, but that of the individual, crime.'

        result = self.ness_auth.get_by_two_way_encryption(url, test_string, node_public, user_private_key, username)

        if result['result'] == 'error':
            print(" ~~~ TEST #2 Two way encryption FAILED ~~~ ")
            print(result['error'])
        else:
            if self.ness_auth.verify_two_way_result(node_verify, result):
                print(" *** TEST #2 Two way encryption OK !!! *** ")
                print(self.ness_auth.decrypt_two_way_result(result, user_private_key))
            else:
                print(" ~~~ TEST #2 Two way encryption FAILED ~~~ ")
                print(" Verifying signature failed ")

                return False

        url = node_url + "/node/joined"

        result = self.ness_auth.get_by_two_way_encryption(url, 'test', node_public, user_private_key, username)

        if result['result'] == 'error':
            print(" ~~~ TEST #3 Registration check FAILED ~~~ ")
            print(result['error'])
        else:
            if self.ness_auth.verify_two_way_result(node_verify, result):
                print(" *** TEST #3 Registration check OK !!! *** ")
                result = self.ness_auth.decrypt_two_way_result(result, user_private_key)
                data = json.loads(result)

                if data['joined']:
                    shadowname = data['shadowname']
                    print(" *** The user:" + username + " is joined with shadowname:" + shadowname + " OK !!! ***")
                else:
                    print("The user:" + username + " is not joined yet.")

                    url = node_url + "/node/join"

                    result = self.ness_auth.get_by_two_way_encryption(url, test_string, node_public, user_private_key, username)

                    if result['result'] == 'error':
                        print(" ~~~ TEST #3.1 Registration FAILED ~~~ ")
                        print(result['error'])
                    else:
                        if self.ness_auth.verify_two_way_result(node_verify, result):
                            print(" *** TEST #3.1 Registration OK *** ")
                            result = self.ness_auth.decrypt_two_way_result(result, user_private_key)
                            print (result)
                            data = json.loads(result)
                            shadowname = data['shadowname']
                            addr = data['address']
                            print("User registered with shadowname:" + shadowname + " and addr:" + addr)
                        else:
                            print(" ~~~ TEST #3.1 Registration FAILED ~~~ ")
                            print(" Verifying signature failed ")


                url = node_url + "/node/test/auth-shadow"

                result = self.ness_auth.get_by_auth_id(url, user_private_key, node_url, node_nonce, username, shadowname, user_nonce)

                if result['result'] == 'error':
                    print(" ~~~ TEST #4 Auth ID with shadowname FAILED ~~~ ")
                    print(result['error'])
                else:
                    print(" *** TEST #4 Auth ID with shadowname OK !!! *** ")
                    print(result['message'])

                test_string = 'Whoever knows how to take, to defend, the thing, to him belongs property'

                result = self.ness_auth.get_by_two_way_encryption(url, test_string, node_public, user_private_key, shadowname)

                if result['result'] == 'error':
                    print(" ~~~ TEST #5 Two way encryption FAILED ~~~ ")
                    print(result['error'])
                else:
                    if self.ness_auth.verify_two_way_result(node_verify, result):
                        print(" *** TEST #5 Two way encryption OK !!! *** ")
                        print(self.ness_auth.decrypt_two_way_result(result, user_private_key))
                    else:
                        print(" ~~~ TEST #5 Two way encryption FAILED ~~~ ")
                        print(" Verifying signature failed ")

            else:
                print(" ~~~ TEST #3 Registration check FAILED ~~~ ")
                print(" Verifying signature failed ")

        return True


print('==Test authentication==')

if ARGS.args(['auth', str, str]):
    tester = AuthTester()

    try:
        tester.test(ARGS.arg(2), ARGS.arg(3))
    except UserNotFound as e:
        print("User '{}' is not in users list".format(e.username))
    except NodeNotFound as e:
        print("NODE '{}' is not in nodes list".format(e.node))
else:
    print('Usage: python test-auth.py <username> <node URL>')