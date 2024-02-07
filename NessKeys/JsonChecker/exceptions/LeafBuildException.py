class LeafBuildException(Exception):
    def __init__(self, key_name, msg, path):
        self.key_name = key_name
        self.path = path
        self.msg = "{}: {} (path: {})".format(key_name, msg, path)
        super().__init__(self.msg)