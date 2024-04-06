import pathlib
from blender_scripts.importer.base import ModelImporter
import os
import bpy


class FBXImporter(ModelImporter):
    def import_file(self, file_path: pathlib.Path) -> None:
        if file_path.suffix == ".fbx":
            bpy.ops.import_scene.fbx(
                filepath=os.path.join(
                    self.file_handler.path_to_files_in_tmp, str(file_path)
                )
            )