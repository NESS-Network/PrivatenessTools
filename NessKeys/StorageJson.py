from NessKeys.interfaces.Storage import Storage
import json, os

class StorageJson(Storage):
    def save(self, keydata: dict, filename: str):
        f = open(filename, "w")
        f.write(json.dumps(keydata, indent=4))
        f.close()

    def restore(self, filename: str) -> dict|bool:
        if not os.path.exists(filename):
            return False
        f = open(filename, "r")
        result = f.read()
        f.close()

        return json.loads(result)