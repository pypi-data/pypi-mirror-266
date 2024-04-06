import os
import pathlib
from blender_scripts.exporter.base import ModelExporter
import bpy


class STLExporter(ModelExporter):
    def export_file(self, file_path: pathlib.Path, newfile_path: str) -> None:
        stl_name: str = newfile_path
        new_path_to_files_stl: str = os.path.join(
            self.file_handler.path_to_public_models, stl_name
        )
        bpy.ops.export_mesh.stl(
            filepath=new_path_to_files_stl, use_mesh_modifiers=True, use_scene_unit=True
        )
