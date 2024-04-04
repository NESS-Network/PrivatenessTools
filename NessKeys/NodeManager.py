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

    def selNode(self, node_url: str):
        self.initKeys()
        fm = Container.FileManager()
        fm.join(self.current_node_username, node_url)

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

        print(" # Current node: " + self.current_node_name)
        return self.NodesService.userinfo()


    def initKeys(self):
        self.KeyManager.initSettings()
        self.KeyManager.initMyNodes()