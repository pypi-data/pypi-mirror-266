import abc
import pathlib

from blender_scripts.filehandler.filehandler import FileHandler


class ModelExporter(abc.ABC):
    def __init__(self, file_handler: FileHandler):
        self.file_handler = file_handler

    @abc.abstractmethod
    def export_file(self, file_path: pathlib.Path, newfile_path: str) -> None:
        pass
