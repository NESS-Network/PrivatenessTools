from .exceptions.LeafBuildException import LeafBuildException
import types

class JsonChecker():
    @staticmethod
    def check(name: str, json: dict, map: dict, path: str = '/'):
        for key in map:
            if not key in json:
                raise LeafBuildException(name, "No '" + key + "' parameter", path + key)
            elif type(map[key]) == list and len(map[key]) != 2:
                raise LeafBuildException(name, "map[" + key + "] must be [type, length]", path + key)
            elif type(map[key]) == list and len(map[key]) == 2 and (map[key][0] != type(json[key]) or map[key][1] != len(json[key])):
                raise LeafBuildException(name, "Key '{}' must have type {} and length {}".format(key, map[key][0], map[key][1]), path + key)
            elif type(map[key]) == dict and type(json[key]) == dict:
                JsonChecker.check(name, json[key], map[key], path + key + '/')
            elif type(map[key]) == type(json[key]):
                if map[key] != json[key]:
                    raise LeafBuildException(name, "{} = {} must be {}".format(key, json[key], map[key]), path + key)
            elif type(map[key]) == dict and type(json[key]) != dict:
                raise LeafBuildException(name, "Wrong type for key '{}' expected <class 'dict'> actualy {}".format(key, type(json[key])), path + key)
            elif type(map[key]) != list and type(map[key]) != types.LambdaType and type(json[key]) != map[key]:
                raise LeafBuildException(name, "Wrong type for key '{}' expected {} actualy {}".format(key, map[key], type(json[key])), path + key)

            elif type(map[key]) == types.LambdaType:
                res = map[key](json[key])
                if res != True:
                    raise LeafBuildException(name, "Key '{}': {}".format(key, res), path + key)