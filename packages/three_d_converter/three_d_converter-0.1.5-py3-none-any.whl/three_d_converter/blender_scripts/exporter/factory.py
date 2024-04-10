import pathlib

from three_d_converter.blender_scripts.filehandler.filehandler import FileHandler
from three_d_converter.blender_scripts.exporter.base import ModelExporter
from three_d_converter.blender_scripts.exporter.fbx import FBXExporter
from three_d_converter.blender_scripts.exporter.gltf_glb import GLTFGLBExporter
from three_d_converter.blender_scripts.exporter.obj import OBJExporter
from three_d_converter.blender_scripts.exporter.stl import STLExporter
from three_d_converter.blender_scripts.exporter.usdz import USDZExporter
from three_d_converter.blender_scripts.exporter.x3d import X3DExporter


class ExporterExtensionFactory:
    @staticmethod
    def get_exporter(
        file_path: pathlib.Path, file_handler: FileHandler
    ) -> ModelExporter:
        if file_path.suffix == ".fbx":
            return FBXExporter(file_handler)
        elif (file_path.suffix == ".gltf") or (file_path.suffix == ".glb"):
            return GLTFGLBExporter(file_handler)
        elif file_path.suffix == ".stl":
            return STLExporter(file_handler)
        elif file_path.suffix == ".obj":
            return OBJExporter(file_handler)
        elif file_path.suffix == ".x3d":
            return X3DExporter(file_handler)
        elif file_path.suffix == ".usdz":
            return USDZExporter(file_handler)
