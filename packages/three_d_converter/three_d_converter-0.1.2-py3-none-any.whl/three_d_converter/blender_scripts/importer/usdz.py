import pathlib
import shutil 
from uuid import uuid4
import zipfile
from blender_scripts.importer.base import ModelImporter
import os
import bpy

class USDZImporter(ModelImporter):
    def import_file(self, file_path: pathlib.Path) -> None:
        newfile_path: str = str(uuid4())
        copied_file_path: str = os.path.join(
            self.file_handler.path_to_public_models, newfile_path + ".usdz"
        )
        shutil.copy2(str(file_path), copied_file_path)

        try:
            with zipfile.ZipFile(str(file_path), "r") as usdz_unzipped:
                usdz_unzipped.extractall(
                    os.path.join(self.file_handler.model_tmp_path_unzip)
                )

            for file_name in os.listdir(self.file_handler.model_tmp_path_unzip):
                if file_name.endswith(".usdc") or file_name.endswith(".usda"):
                    bpy.ops.wm.usd_import(
                        filepath=os.path.join(
                            self.file_handler.model_tmp_path_unzip, file_name
                        ),
                        import_materials=True,
                        import_usd_preview=True,
                        import_subdiv=True,
                        read_mesh_colors=True,
                        mtl_name_collision_mode="REFERENCE_EXISTING",
                    )
                else:
                    print(f"Unsupported file format {file_name}")
        finally:
            os.remove(copied_file_path)