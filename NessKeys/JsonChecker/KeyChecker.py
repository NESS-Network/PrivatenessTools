from .exceptions.LeafBuildException import LeafBuildException
import types

class KeyChecker():
    @staticmethod
    def check(name: str, json: dict, key: str, path: str = '/'):
        if not key in json:
            raise LeafBuildException(name, "No '" + key + "' parameter", path + key)
