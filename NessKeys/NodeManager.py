from NessKeys.KeyManager import KeyManager
import NessKeys.Prng as prng

from NessKeys.exceptions.NodeNotSelected import NodeNotSelected

from base64 import b64encode
from base64 import b64decode
import uuid

from services.node import node

class NodeManager:

    def __init__(self, KeyManager: KeyManager, NodesService: node):
        self.KeyManager = KeyManager
        self.NodesService = NodesService
        self.current_node_name = self.KeyManager.getCurrentNodeName()
        self.current_node_username = self.KeyManager.getCurrentUser()

    def getCurrentNodeName(self):
        return self.current_node_name

    def getCurrentNodeUsername(self):
        return self.current_node_username

    def listNodes(self):
        self.initKeys()
        return self.KeyManager.getNodesList()

    def listNodesFull(self, network = '', service = '', sort = '', reverse_sort = False):
        self.initKeys()
        nodes = self.listNodes()
        current_node = self.getCurrentNodeName()
        nodes = self.KeyManager.getNodesList()
        Result = []

        def fn_sort(row):
            if reverse_sort and type(row[sort]) == int:
                return -row[sort]
            else:
                return row[sort]

        for node in nodes:
            if self.nodePing(node['url']):
                if network == '' or node['network'] == network.lower():
                    if service == '' or service in node['services']:
                        node_caption = node['url']
                        if current_node == node['url']:
                            node_caption = '==> ' +node['url'] + ' <=='

                        node_info = self.NodesService.nodeInfo(node['url'])

                        row = {'caption': node_caption, \
                            'network': node['network'], \
                            'services': ','.join(node['services']), \
                            'tariff': node['tariff'], \
                            'slots': "{} ({})".format(node_info['slots'], node_info['slots_free']), \
                            'slots_free': node_info['slots_free'], \
                            'quota': node_info['files']['quota'] }

                        Result.append(row)

        if sort != '':
            Result.sort(key = fn_sort)
        else:
            Result.sort()

        return Result

    def selNode(self, node_url: str):
        self.initKeys()
        fm = Container.FileManager()
        fm.join(self.current_node_username, node_url)

    def nodePing(self, node_url: str) -> dict:
        return self.NodesService.nodePing(node_url)

    def info(self, node_url: str):
        self.initKeys()
        
        return self.NodesService.nodeInfo(node_url)

    def about(self, node_url: str):
        self.initKeys()
        
        return self.NodesService.about(node_url)

    def userinfo(self):
        self.initKeys()

        if self.current_node_name == False:
            raise NodeNotSelected()

        print(" # User {} on node {} ".format(self.current_node_username, self.current_node_name) )
        return self.NodesService.userinfo()


    def initKeys(self):
        self.KeyManager.initSettings()
        self.KeyManager.initMyNodes()