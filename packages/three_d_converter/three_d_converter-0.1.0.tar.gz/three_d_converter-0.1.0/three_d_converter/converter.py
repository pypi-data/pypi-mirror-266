import subprocess
import pathlib
from uuid import uuid4


class Converter:
    @staticmethod
    def convert_model(input_file: str, output_file: str) -> None:
        SCRIPT_PATH = pathlib.Path(__file__).parent / "blender_scripts" / "main.py"

        blender_command = [
            "blender",
            "-b",
            "-noaudio",
            "--python",
            SCRIPT_PATH.resolve().as_posix(),
            "--",
            input_file,
            output_file,
        ]
        subprocess.run(blender_command)

