import os
import pathlib
from blender_scripts.exporter.base import ModelExporter
import bpy

class X3DExporter(ModelExporter):
    def export_file(self, file_path: pathlib.Path, newfile_path: str) -> None:
        x3d_name: str = newfile_path
        new_path_to_files_x3d: str = os.path.join(
            self.file_handler.path_to_public_models, x3d_name
        )
        bpy.ops.export_scene.x3d(filepath=new_path_to_files_x3d)
