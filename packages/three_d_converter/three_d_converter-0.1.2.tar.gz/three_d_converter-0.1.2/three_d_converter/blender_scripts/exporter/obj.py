import os
from blender_scripts.exporter.base import ModelExporter
import pathlib
import bpy

class OBJExporter(ModelExporter):
    def export_file(self, file_path: pathlib.Path, newfile_path: str) -> None:
        obj_name: str = newfile_path

        new_path_to_files_obj: str = os.path.join(
            self.file_handler.path_to_public_models, obj_name
        )

        bpy.ops.export_scene.obj(
            filepath=new_path_to_files_obj, use_mesh_modifiers=True
        )
