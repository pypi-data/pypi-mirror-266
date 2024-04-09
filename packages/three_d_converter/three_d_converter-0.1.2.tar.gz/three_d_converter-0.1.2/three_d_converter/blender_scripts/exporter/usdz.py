import os
import pathlib
import zipfile
from blender_scripts.exporter.base import ModelExporter
import bpy


class USDZExporter(ModelExporter):
    def export_file(self, file_path: pathlib.Path, newfile_path: str) -> None:
        usdc_name: str = "main" + ".usdc"
        usdz_name: str = newfile_path
        new_path_to_files_usdc: str = os.path.join(
            self.file_handler.model_tmp_path_export, usdc_name
        )
        new_path_to_files_usdz: str = usdz_name
        new_path_to_files_usdz: str = os.path.join(
            self.file_handler.path_to_public_models, usdz_name
        )
        self.export_usdz(new_path_to_files_usdc, new_path_to_files_usdz)

    def export_usdz(
        self, new_path_to_files_usdc: str, new_path_to_files_usdz: str
    ) -> None:
        bpy.ops.wm.usd_export(
            filepath=new_path_to_files_usdc,
            check_existing=False,
            export_materials=True,
            export_textures=True,
            visible_objects_only=False,
            overwrite_textures=True,
            export_animation=True,
            export_hair=True,
        )
        usdz: zipfile.ZipFile = zipfile.ZipFile(new_path_to_files_usdz, "w")
        usdz.write(
            new_path_to_files_usdc,
            pathlib.Path(new_path_to_files_usdc).name,
            compress_type=None,
            compresslevel=None,
        )
        os.remove(new_path_to_files_usdc)

        self.write_dir(self.file_handler.model_tmp_path_export, usdz)

        usdz.close()

    def write_dir(self, dir: str, usdz: zipfile.ZipFile, arc_path: str = "") -> None:
        for file in os.listdir(dir):
            cur_path: str = os.path.join(dir, file)
            cur_arc_path: str = os.path.join(arc_path, file)

            if pathlib.Path(cur_path).is_dir():
                self.write_dir(cur_path, usdz, cur_arc_path)
                continue

            usdz.write(cur_path, cur_arc_path, compress_type=None, compresslevel=None)
