import sys
import os
print(sys.path)
# Add the parent directory of NessKeys to the module search path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, parent_dir)

from flask import Flask, render_template
from NessKeys.KeyManager import KeyManager
from NessKeys.StorageJson import StorageJson
from NessKeys.KeyMakerNess import KeyMakerNess
from NessKeys.FileManager import FileManager
from NessKeys.NodeManager import NodeManager
from NessKeys.ConsoleOutput import ConsoleOutput
from NessKeys.interfaces.output import output
from services.node import node
from services.files import files

app = Flask(__name__, template_folder='../services/web')

class Container:
    def KeyManager(self) -> KeyManager:
        storage = StorageJson()
        maker = KeyMakerNess()
        return KeyManager(storage, maker)
    
    def NodeService(self) -> node:
        km = self.KeyManager()
        return node(km.getUsersKey(), km.getNodesKey(), km.getMyNodesKey(), self.output())

    def FilesService(self) -> files:
        km = self.KeyManager()
        return files(km.getUsersKey(), km.getNodesKey(), km.getMyNodesKey(), km.getFilesKey(), km.getDirectoriesKey(), km.getBackupKey(), self.output())

    def NodeManager(self) -> NodeManager:
        return NodeManager(self.KeyManager(), self.NodeService())

    def FileManager(self) -> FileManager:
        def ns():
            return self.NodeService()

        def fs():
            return self.FilesService()

        return FileManager(self.KeyManager(), ns, fs)

    def output(self) -> output:
        return ConsoleOutput()

    def get_node_list(self):
        km = self.KeyManager()
        node_service = self.NodeService()
        node_list = node_service.get_nodes()
        return node_list


@app.route('/')
def index():
    container = Container()
    node_list = container.get_node_list()
    return render_template('index.html', node_list=node_list)


if __name__ == '__main__':
    app.run(debug=True)