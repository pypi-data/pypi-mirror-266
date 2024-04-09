import pathlib
from blender_scripts.importer.base import ModelImporter
import bpy


class FBXImporter(ModelImporter):
    def import_file(self, file_path: pathlib.Path) -> None:
        if file_path.suffix == ".fbx":
            bpy.ops.import_scene.fbx(filepath=str(file_path))