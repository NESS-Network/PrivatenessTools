class UserNotFound(Exception):
    def __init__(self, username: str):
        self.username = username