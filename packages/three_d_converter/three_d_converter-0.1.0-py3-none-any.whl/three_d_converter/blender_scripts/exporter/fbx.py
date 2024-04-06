import os
import pathlib
from blender_scripts.exporter.base import ModelExporter
import bpy

class FBXExporter(ModelExporter):
    def export_file(self, file_path: pathlib.Path, newfile_path: str) -> None:
        fbx_name: str = newfile_path
        new_path_to_files_fbx: str = os.path.join(
            self.file_handler.path_to_public_models, fbx_name
        )
        bpy.ops.export_scene.fbx(filepath=new_path_to_files_fbx)

