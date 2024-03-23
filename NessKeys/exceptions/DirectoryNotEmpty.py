class DirectoryNotEmpty(Exception):
    def __init__(self, name: int):
        self.name = name