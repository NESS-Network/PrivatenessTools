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

from NessKeys.interfaces.output import output as ioutput

class node:
    def __init__(self, Users: Users, nodes: Nodes, myNodes: MyNodes, output: ioutput):

        self.Users = Users
        self.Nodes = nodes
        self.MyNodes = myNodes

        current_node = self.MyNodes.getCurrentNode()

        if len(current_node) == 2:
            self.username = current_node[0]
            self.node_name = current_node[1]
        else:
            self.username = ''
            self.node_name = ''

        self.auth = NessAuth()

        self.output = output

    def nodePing(self, node_url: str) -> dict:
        r = requests.get(node_url + '/node/nodes', verify=False)

        if r.status_code != 200:
            return False

        try:
            json.loads(r.text)
        except Exception as e:
            return False

        return True

    def nodeInfo(self, node_url: str) -> dict:
        info = requests.get(node_url + '/node/info', verify=False).text

        try:
            info = json.loads(info)
        except Exception as e:
            return False

        if info['result'] != 'error':
            return info['info']
        else:
            return False


    def nodesList(self, node_url: str) -> dict:
        return json.loads(requests.get(node_url + '/node/about', verify=False).text)

    def about(self, node_url: str) -> dict:
        return requests.get(node_url + '/node/about', verify=False).text

    def join(self, node_name: str):
        currentNode = self.Nodes.findNode(node_name)

        if currentNode == False:
            raise NodeNotFound(node_name)

        url = currentNode['url'] + "/node/join"

        result = self.auth.get_by_two_way_encryption(
            url, 
            '123', 
            currentNode['public'], 
            self.Users.getPrivateKey(), 
            self.Users.getUsername() )

        if result['result'] == 'error':
            raise NodeError()

        if not self.auth.verify_two_way_result(currentNode['verify'], result):
            raise AuthError()

        result = self.auth.decrypt_two_way_result(result, self.Users.getPrivateKey())
        data = json.loads(result)
        
        return data['shadowname']

    def withdraw(self, node_name: str, coins: float, hours: int, to_addr: str):
        currentNode = self.Nodes.findNode(node_name)

        if currentNode == False:
            raise NodeNotFound(node_name)

        shadowname = self.joined(node_name)

        if shadowname == False:
            raise UserNotFound(self.username)

        wdata = json.dumps({'coins': coins, 'hours': hours, 'to_addr': to_addr})
        url = currentNode['url'] + "/node/withdraw"

        result = self.auth.get_by_two_way_encryption(
            url, 
            wdata, 
            currentNode['public'], 
            self.Users.getPrivateKey(), 
            shadowname )

        if result['result'] == 'error':
            raise NodeError(result['error'])

        if not self.auth.verify_two_way_result(currentNode['verify'], result):
            raise AuthError(result['error'])

        result = self.auth.decrypt_two_way_result(result, self.Users.getPrivateKey())

        # result = json.loads(result)
        
        print(" *** Withdraw OK *** ")
        print("Nodes answer: ")
        print(result)

        return True

    def joined(self, node_name: str):
        currentNode = self.Nodes.findNode(node_name)

        if currentNode == False:
            raise NodeNotFound(node_name)

        url = currentNode['url'] + "/node/joined"

        result = self.auth.get_by_two_way_encryption(
            url, 
            '123', 
            currentNode['public'], 
            self.Users.getPrivateKey(), 
            self.Users.getUsername() )

        if result['result'] == 'error':
            raise NodeError(result['error'])
        
        if not self.auth.verify_two_way_result(currentNode['verify'], result):
            raise AuthError()

        result = self.auth.decrypt_two_way_result(result, self.Users.getPrivateKey())
        data = json.loads(result)

        if data['joined']:
            return data['shadowname']
        else:
            return False

    def exist(self, node_url: str, username: str) -> bool:
        result = requests.get(node_url + '/node/exist/' + username, verify=False).text
        result = json.loads(result)
        return result['info']['exists']

    def userinfo(self):
        myNode = self.MyNodes.findNode(self.username, self.node_name)
        currentNode = self.Nodes.findNode(self.node_name)

        if currentNode == False:
            raise NodeNotFound(self.node_name)

        shadowname = myNode['shadowname']

        url = currentNode['url'] + "/node/userinfo"

        result = self.auth.get_by_two_way_encryption(
            url, 
            '123', 
            currentNode['public'], 
            self.Users.getPrivateKey(), 
            shadowname )


        if result['result'] == 'error':
            raise NodeError(result['error'])

        if not self.auth.verify_two_way_result(currentNode['verify'], result):
            raise AuthError()

        result = self.auth.decrypt_two_way_result(result, self.Users.getPrivateKey())
        data = json.loads(result)

        return data
