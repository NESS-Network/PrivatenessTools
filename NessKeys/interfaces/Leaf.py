import json
from abc import ABC, abstractmethod 

class Leaf():
    @abstractmethod
    def compile(self) -> dict:
        pass

    @abstractmethod
    def serialize(self) -> str:
        return json.dumps(self.compile())