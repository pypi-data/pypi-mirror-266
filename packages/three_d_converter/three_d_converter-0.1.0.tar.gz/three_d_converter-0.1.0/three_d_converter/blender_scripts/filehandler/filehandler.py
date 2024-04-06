import os
import shutil
from uuid import uuid4

class FileHandler: 
    def __init__(
        self,
        path_to_files_in_tmp: str = "./tmp",
        path_to_public_models: str = "",
    ):  
        self.path_to_files_in_tmp: str = path_to_files_in_tmp
        self.path_to_public_models: str = path_to_public_models

    def __enter__(self):
        print("entered")
        self.model_tmp_path: str = os.path.join(self.path_to_files_in_tmp, f"{uuid4()}")
        self.model_tmp_path_unzip: str = os.path.join(self.model_tmp_path, "unzipped")
        self.model_tmp_path_export: str = os.path.join(self.model_tmp_path, "export")
        os.makedirs(self.model_tmp_path)
        os.makedirs(self.model_tmp_path_unzip)
        os.makedirs(self.model_tmp_path_export)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        print("cleaned up!")

    def cleanup(self) -> None:
        shutil.rmtree(self.model_tmp_path)