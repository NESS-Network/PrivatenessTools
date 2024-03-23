from framework.Container import Container
from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException
from ..keys.Backup import Backup
from ..keys.Files import Files
from ..keys.Directories import Directories
from ..keys.Settings import Settings
import json
import random
import uuid

print("== *** ==")

fs = Container.FilesService()
print( fs.fileExists('asdfsfgherg3u0tjgteog') )
print( fs.fileExists('spmo.53') )

fm = Container.FileManager()