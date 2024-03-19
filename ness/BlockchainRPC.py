import requests
import json
import time

class BlockchainRPC:

    def __init__(self, url: str, port: int, login: str, password: str):
        """
        :param url:
        :param port:
        :param login:
        :param password:
        """
        self.url = url
        self.port = port
        self.login = login
        self.password = password

    def get_info(self):
        return self.__method("getinfo", [])

    def check(self):
        try:
            self.get_info()
        except Exception:
            return False

        return True


    def __get_url(self):
        return "http://{}:{}@{}:{}/".format(self.login, self.password, self.url, self.port)

    def __method(self, method, params):
        url = self.__get_url()

        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }

        response = requests.post(url, json=payload)
        response = requests.post(url, json=payload).json()

        return response

    def showResource(self, name):
        return self.__method("name_show", [name, '', 'base64'])

    def listNodes(self):
        return self.__method("name_filter", ['^worm:node:ness:.+', 0, 0, 0, '', ''])