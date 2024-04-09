import abc
import pathlib

from blender_scripts.filehandler.filehandler import FileHandler


class ModelImporter(abc.ABC):
    def __init__(self, file_handler: FileHandler):
        self.file_handler = file_handler

    @abc.abstractmethod
    def import_file(self, file_path: pathlib.Path) -> None:
        pass

