class NodeNotSelected(Exception):
    def __init__(self, node_url: str):
        self.node_url = node_url