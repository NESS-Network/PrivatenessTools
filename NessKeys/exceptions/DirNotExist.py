class DirNotExist(Exception):
    def __init__(self, id: int):
        self.id = id