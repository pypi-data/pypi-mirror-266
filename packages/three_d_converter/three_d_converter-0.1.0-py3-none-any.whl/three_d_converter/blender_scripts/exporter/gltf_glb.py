import os
import pathlib
from blender_scripts.exporter.base import ModelExporter
import bpy


class GLTFGLBExporter(ModelExporter):
    def export_file(self, file_path: pathlib.Path, newfile_path: str) -> None:
        gltf_name: str = newfile_path

        new_path_to_files_gltf: str = os.path.join(
            self.file_handler.path_to_public_models, gltf_name
        )

        bpy.ops.export_scene.gltf(
            filepath=new_path_to_files_gltf,
            export_format="GLTF_EMBEDDED",
            export_animations=True,
            export_materials="EXPORT",
        )
