import pathlib

from three_d_converter.blender_scripts.filehandler.filehandler import FileHandler
from three_d_converter.blender_scripts.importer.base import ModelImporter
from three_d_converter.blender_scripts.importer.fbx import FBXImporter
from three_d_converter.blender_scripts.importer.gltf_glb import GLTFGLBImporter
from three_d_converter.blender_scripts.importer.obj import OBJImporter
from three_d_converter.blender_scripts.importer.stl import STLImporter
from three_d_converter.blender_scripts.importer.usdz import USDZImporter
from three_d_converter.blender_scripts.importer.x3d import X3DImporter


class ImporterExtensionFactory:
    @staticmethod
    def get_importer(file_path: pathlib.Path, file_handler: FileHandler) -> ModelImporter:
        if file_path.suffix == ".fbx": 
            return FBXImporter(file_handler)
        elif (file_path.suffix == ".gltf") or (file_path.suffix == ".glb"):
            return GLTFGLBImporter(file_handler)
        elif file_path.suffix == ".stl":
            return STLImporter(file_handler)
        elif file_path.suffix == ".obj":
            return OBJImporter(file_handler)
        elif file_path.suffix == ".x3d":
            return X3DImporter(file_handler)
        elif file_path.suffix == ".usdz":
            return USDZImporter(file_handler)