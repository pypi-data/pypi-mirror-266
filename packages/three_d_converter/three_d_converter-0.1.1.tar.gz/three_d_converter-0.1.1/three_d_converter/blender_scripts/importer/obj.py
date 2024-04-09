import pathlib
from blender_scripts.importer.base import ModelImporter
import bpy

class OBJImporter(ModelImporter):
    def import_file(self, file_path: pathlib.Path) -> None:
        if file_path.suffix == ".obj":
            bpy.ops.import_scene.obj(filepath=str(file_path))