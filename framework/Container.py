from NessKeys.KeyManager import KeyManager
from NessKeys.StorageJson import StorageJson
from NessKeys.KeyMakerNess import KeyMakerNess
from NessKeys.FileManager import FileManager
from NessKeys.NodeManager import NodeManager

from services.node import node
from services.files import files

from NessKeys.interfaces.output import output as ioutput

from NessKeys.ConsoleOutput import ConsoleOutput


class Container:
    def KeyManager() -> KeyManager:
        storage = StorageJson()
        maker = KeyMakerNess()
        return KeyManager(storage, maker)

    def NodeService() -> node:
        km = Container.KeyManager()
        return node(km.getUsersKey(), km.getNodesKey(), km.getMyNodesKey(), Container.output())

    def FilesService() -> files:
        km = Container.KeyManager()
        return files(km.getUsersKey(), km.getNodesKey(), km.getMyNodesKey(), km.getFilesKey(), km.getDirectoriesKey(), km.getBackupKey(), Container.output())

    def NodeManager() -> NodeManager:
        return NodeManager(Container.KeyManager(), Container.NodeService())

    def FileManager() -> FileManager:
        def ns ():
             return Container.NodeService()
        def fs ():
             return Container.FilesService()
             
        return FileManager(Container.KeyManager(), ns, fs)

    def output() -> output:
        return ConsoleOutput()
