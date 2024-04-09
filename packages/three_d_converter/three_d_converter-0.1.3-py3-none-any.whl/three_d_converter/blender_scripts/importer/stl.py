import pathlib
from three_d_converter.blender_scripts.importer.base import ModelImporter
import bpy

class STLImporter(ModelImporter):
    def import_file(self, file_path: pathlib.Path) -> None:
        if file_path.suffix == ".stl":
            bpy.ops.import_mesh.stl(filepath=str(file_path))