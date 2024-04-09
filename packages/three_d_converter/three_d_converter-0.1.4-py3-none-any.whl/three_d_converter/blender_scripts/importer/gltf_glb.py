import pathlib
from three_d_converter.blender_scripts.importer.base import ModelImporter
import bpy

class GLTFGLBImporter(ModelImporter):
    def import_file(self, file_path: pathlib.Path) -> None:
        if (file_path.suffix == ".gltf") or (file_path.suffix == ".glb"):
            bpy.ops.import_scene.gltf(filepath=str(file_path))