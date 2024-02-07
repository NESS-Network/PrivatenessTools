from NessKeys.interfaces.NessKey import NessKey
from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.DeepChecker import DeepChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException

class Directories(NessKey):

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

        DeepChecker.check('Directories (directories list)', keydata, map, 3)

        self.__directories = keydata["directories"]
        self.__current = keydata["current"]
        
    def compile(self) -> dict:
        appdata = {
            "filedata": {
                "vendor": "Privateness",
                "type": "service",
                "for": "files-directories"
            },
            "directories": self.__directories,
            "current": self.__current
        }

        return appdata

    def worm(self) -> str:
        return ""
        
    def nvs(self) -> str:
        return ""

    def print(self):
        return "Privateness Directories storage file"

    def filename():
        return "directories.json"

    def getFilename(self):
        return "directories.json"
        
    def get(self, node_name: str, id: int):
        id = str(id)
        if id in self.__directories[node_name]:
            return self.__directories[node_name][str(id)]
        else:
            return False
        
    def get_parent_id(self, node_name: str, id: int):
        return self.__directories[node_name][str(id)]['parent_id']
        
    def mkdir(self, node_name: str, parent_id: int, name: str):
        top_id = 0

        for id in self.__directories[node_name]:
            id = int(id)
            if id > top_id:
                top_id = id

        top_id += 1

        self.__directories[node_name][top_id] = {
            'parent_id': parent_id,
            'name': name
        }

    def initDirectories(self, node_name: str):
        if not node_name in self.__directories:
            self.__directories[node_name] = {0 : {'name': '', 'parent_id': 0}}

        if not node_name in self.__current:
            self.__current[node_name] = 0

    def getCurrentDir(self, node_name: str):
        if node_name in self.__current:
            return self.__current[node_name]
        else:
            return 0

    def getCurrentName(self, node_name: str):
        return self.path(node_name)
        
    def move(self, node_name: str, id: int, new_parent_id: int):
        self.__directories[node_name][str(id)]['parent_id'] = new_parent_id
        
    def rename(self, node_name: str, id: int, new_name: str):
        self.__directories[node_name][str(id)]['name'] = new_name
        
    def cd(self, node_name: str, id: int):
        self.__current[node_name] = id
        
    def up(self, node_name: str):
        self.__current[node_name] = self.__directories[node_name][self.__current][node_name]['parent_id']
        
    def top(self, node_name: str):
        self.__current[node_name] = 0

    
        
    def path(self, node_name: str):
        current = str(self.__current[node_name])
        path = [self.__directories[node_name][current]['name']]

        for id in self.__directories[node_name]:
            if current == '0':
                path.reverse()
                break
            else:
                current = str(self.__directories[node_name][current]['parent_id'])
                path.append(self.__directories[node_name][current]['name'])

        if len(path) == 1:
            return '/'

        return '/'.join(path)

    
    def getDirectories(self, node_name: str, parent_id: int):
        dir_list = {}

        for id in self.__directories[node_name]:
            if int(id) != 0:
                if self.__directories[node_name][id]['parent_id'] == int(parent_id):
                    dir_list[id] = self.__directories[node_name][id]
                
        return dir_list

        
    def ls(self, node_name: str):
        dir_list = {}
        current_dir = str(self.__current[node_name])

        if int(current_dir) != 0:
            parent_dir = self.__directories[node_name][current_dir]['parent_id']
            dir_list[parent_dir] = {'name': '..'}
            
        for id in self.__directories[node_name]:
            if int(id) != 0:
                if self.__directories[node_name][id]['parent_id'] == int(current_dir):
                    dir_list[id] = self.__directories[node_name][id]
                
        return dir_list

    def __lsr(self, node_name: str, parent_id: int):
        dir_list = []

        for id in self.__directories[node_name]:
            if self.__directories[node_name][id]['parent_id'] == parent_id:
                dir_list.append(self.__directories[node_name][id])
                dir_list.extend(self.__lsr(id))

        return dir_list
        
    def ls_recursive(self, node_name: str):
        return self.__lsr(self.__current[node_name])

    def __tree(self, node_name: str, parent_id: int):
        dir_list = {}

        for id in self.__directories[node_name]:
            if int(id) != 0:
                if self.__directories[node_name][id]['parent_id'] == parent_id:
                    dir_list[id] = self.__directories[node_name][id]
                    children = self.__tree(node_name, int(id))

                    if len(children) != 0:
                        dir_list[id]['children'] = children

        return dir_list
        
    def tree(self, node_name: str):
        root = self.__directories[node_name]['0']
        root['name'] = '/'
        root['children'] = self.__tree(node_name, 0)

        return { '0': root }
        
    def remove(self, node_name: str, id: int):
        del self.__directories[node_name][str(id)]
