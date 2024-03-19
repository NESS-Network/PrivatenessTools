from NessKeys.interfaces.NessKey import NessKey
from NessKeys.exceptions.DirNotExist import DirNotExist
from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.DeepChecker import DeepChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException

class Directories(NessKey):
    __directories = {}
    __current = {}

    def load(self, keydata: dict):
        map = {
            "filedata": {
                "vendor": "Privateness",
                "type": "service",
                "for": "files-directories"
            },
            "directories": dict,
            "current": dict
        }

        JsonChecker.check('Directories', keydata, map)

        map = {
            'name': str,
            'parent_id': int
        }

        DeepChecker.check('Directories (directories list)', keydata, map, 4)

        self.__directories = keydata["directories"]
        self.__current = keydata["current"]
        
    def compile(self) -> dict:
        keydata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "service",
                "for": "files-directories"
            },
            "directories": self.__directories,
            "current": self.__current
        }

        return keydata

    def worm(self) -> str:
        return ""
        
    def nvs(self) -> str:
        return ""

    def print(self):
        return "Privateness Directories storage file"

    def filename():
        return "directories.key.json"

    def getFilename(self):
        return "directories.key.json"

    def initDirectories(self, username: str, node_name: str):
        if not username in self.__directories:
            self.__directories[username] = {}

        if not node_name in self.__directories[username]:
            self.__directories[username][node_name] = {0 : {'name': '', 'parent_id': 0}}

        if not username in self.__current:
            self.__current[username] = {}

        if not node_name in self.__current[username]:
            self.__current[username][node_name] = 0
        
    def get(self, username: str, node_name: str, id: int):
        self.initDirectories(username, node_name)

        if str(id) in self.__directories[username][node_name]:
            return self.__directories[username][node_name][str(id)]
        else:
            raise DirNotExist(id)
        
    def get_parent_id(self, username: str, node_name: str, id: int):
        self.initDirectories(username, node_name)

        if not str(id) in self.__directories[username][node_name]:
            raise DirNotExist(id)

        return self.__directories[username][node_name][str(id)]['parent_id']
        
    def mkdir(self, username: str, node_name: str, parent_id: int, name: str) -> int:
        self.initDirectories(username, node_name)

        top_id = 0

        for id in self.__directories[username][node_name]:
            id = int(id)
            if id > top_id:
                top_id = id

        top_id += 1

        self.__directories[username][node_name][top_id] = {
            'parent_id': parent_id,
            'name': name
        }

        return top_id

    def getCurrentDir(self, username: str, node_name: str):
        self.initDirectories(username, node_name)
            
        return self.__current[username][node_name]

    def getCurrentName(self, username: str, node_name: str):
        return self.path(username, node_name)
        
    def move(self, username: str, node_name: str, id: int, new_parent_id: int):
        self.initDirectories(username, node_name)

        if not str(id) in self.__directories[username][node_name]:
            raise DirNotExist(id)

        self.__directories[username][node_name][str(id)]['parent_id'] = new_parent_id
        
    def rename(self, username: str, node_name: str, id: int, new_name: str):
        self.initDirectories(username, node_name)

        if not str(id) in self.__directories[username][node_name]:
            raise DirNotExist(id)

        self.__directories[username][node_name][str(id)]['name'] = new_name
        
    def cd(self, username: str, node_name: str, id: int):
        self.initDirectories(username, node_name)

        if not str(id) in self.__directories[username][node_name]:
            raise DirNotExist(id)

        self.__current[username][node_name] = id
        
    def up(self, username: str, node_name: str):
        self.initDirectories(username, node_name)

        self.__current[username][node_name] = self.__directories[username][node_name][self.__current][username][node_name]['parent_id']
        
    def top(self, username: str, node_name: str):
        self.initDirectories(username, node_name)

        self.__current[username][node_name] = 0

    def path(self, username: str, node_name: str):
        self.initDirectories(username, node_name)

        current = str(self.__current[username][node_name])
        path = [self.__directories[username][node_name][current]['name']]

        for id in self.__directories[username][node_name]:
            if current == '0':
                path.reverse()
                break
            else:
                current = str(self.__directories[username][node_name][current]['parent_id'])
                path.append(self.__directories[username][node_name][current]['name'])

        if len(path) == 1:
            return '/'

        return '/'.join(path)

    
    def getDirectories(self, username: str, node_name: str, parent_id: int):
        self.initDirectories(username, node_name)

        if not str(parent_id) in self.__directories[username][node_name]:
            raise DirNotExist(parent_id)

        dir_list = {}

        for id in self.__directories[username][node_name]:
            if int(id) != 0:
                if self.__directories[username][node_name][id]['parent_id'] == int(parent_id):
                    dir_list[id] = self.__directories[username][node_name][id]
                
        return dir_list

        
    def ls(self, username: str, node_name: str):
        self.initDirectories(username, node_name)

        dir_list = {}
        current_dir = str(self.__current[username][node_name])

        if int(current_dir) == 0:
            dir_list[0] = {'name': '.'}
        else:
            parent_dir = self.__directories[username][node_name][current_dir]['parent_id']
            dir_list[parent_dir] = {'name': '..'}
            
        for id in self.__directories[username][node_name]:
            if int(id) != 0:
                if self.__directories[username][node_name][id]['parent_id'] == int(current_dir):
                    dir_list[id] = self.__directories[username][node_name][id]
                
        return dir_list

    def __lsr(self, username: str, node_name: str, parent_id: int):
        self.initDirectories(username, node_name)

        if not str(parent_id) in self.__directories[username][node_name]:
            raise DirNotExist(parent_id)

        dir_list = []

        for id in self.__directories[username][node_name]:
            if self.__directories[username][node_name][id]['parent_id'] == parent_id:
                dir_list.append(self.__directories[username][node_name][id])
                dir_list.extend(self.__lsr(id))

        return dir_list
        
    def ls_recursive(self, username: str, node_name: str):
        self.initDirectories(username, node_name)

        return self.__lsr(self.__current[username][node_name])

    def __tree(self, username: str, node_name: str, parent_id: int):
        self.initDirectories(username, node_name)

        if not str(parent_id) in self.__directories[username][node_name]:
            raise DirNotExist(parent_id)

        dir_list = {}

        for id in self.__directories[username][node_name]:
            if int(id) != 0:
                if self.__directories[username][node_name][id]['parent_id'] == parent_id:
                    dir_list[id] = self.__directories[username][node_name][id]
                    children = self.__tree(username, node_name, int(id))

                    if len(children) != 0:
                        dir_list[id]['children'] = children

        return dir_list
        
    def tree(self, username: str, node_name: str):
        self.initDirectories(username, node_name)

        root = self.__directories[username][node_name]['0']
        root['name'] = '/'
        root['children'] = self.__tree(username, node_name, 0)

        return { '0': root }
        
    def remove(self, username: str, node_name: str, id: int):
        self.initDirectories(username, node_name)

        if not str(id) in self.__directories[username][node_name]:
            raise DirNotExist(id)

        del self.__directories[username][node_name][str(id)]
