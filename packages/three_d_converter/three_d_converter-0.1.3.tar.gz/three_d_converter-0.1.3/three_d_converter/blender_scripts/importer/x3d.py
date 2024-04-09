import pathlib
from three_d_converter.blender_scripts.importer.base import ModelImporter
import bpy

class X3DImporter(ModelImporter):
    def import_file(self, file_path: pathlib.Path) -> None:
        if file_path.suffix == ".x3d":
            bpy.ops.import_scene.x3d(filepath=str(file_path))