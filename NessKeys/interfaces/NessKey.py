from NessKeys.interfaces.Leaf import Leaf
from abc import ABC, abstractmethod 
import json

class NessKey(Leaf):
    @abstractmethod
    def load(self, keydata: dict):
        pass

    @abstractmethod
    def print(self):
        pass

    @abstractmethod
    def getFilename(self):
        pass
    
    @abstractmethod
    def worm(self):
        pass
    
    @abstractmethod
    def nvs(self):
        pass