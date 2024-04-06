import subprocess
import platform
import shutil


class BlenderRunner:
    blender_path = None

    def __init__(self):
        self.blender_installation_check()

    def blender_installation_check(self):
        self.blender_path = shutil.which("blender")
        if self.blender_path:
            print(f"Blender is already installed at {self.blender_path}")
        else:
            print("Blender is not installed or not found in the system PATH.")


def check_blender_installation():
    try:
        result = subprocess.run(
            ["blender", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            print("Blender is already installed.")
            print(result.stdout.decode("utf-8"))
        else:
            print("Blender is not installed.")
            install_blender()

    except Exception as e:
        print("An error occured ", e)


def install_homebrew():
    try:
        result = subprocess.run(
            ["brew", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            print("Homebrew is already installed.")
            print(result.stdout.decode("utf-8"))
        else:
            print("Homebrew is not installed.")
            subprocess.run(
                [
                    "/bin/bash",
                    "-c",
                    "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)",
                ]
            )
    except Exception as e:
        print("An error occured ", e)


def install_blender():
    os_name = platform.system()
    if os_name == "Darwin":
        install_homebrew()
        subprocess.run(["brew", "install", "blender"])
    elif os_name == "Linux":
        subprocess.run(["sudo", "apt", "install", "blender"])
    else:
        print("OS not supported")

