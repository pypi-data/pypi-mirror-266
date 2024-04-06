import argparse
import pathlib
import sys 
import os
import bpy

class ModelConvertParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("error: %s\n" % message)
        self.print_help()
        sys.exit(2)


def get_parser():
    parser = ModelConvertParser(description="Convert 3D files to other formats")
    parser.add_argument("input", type=str, help="Path to the input file")
    parser.add_argument("output", type=str, help="Path to the output file")
    return parser


def main():
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    # tell python where to find the module
    MODULE_PATH = pathlib.Path(__file__).parent.parent
    sys.path.append(str(MODULE_PATH.resolve()))

    from blender_scripts.importer.factory import ImporterExtensionFactory
    from blender_scripts.exporter.factory import ExporterExtensionFactory
    from blender_scripts.filehandler.filehandler import FileHandler

    script_args = sys.argv[sys.argv.index("--") + 1 :]

    args = get_parser().parse_args(script_args)
    input_file = args.input
    output_file = args.output

    output_dir, output_filename = os.path.split(output_file)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, output_filename)


    with FileHandler() as file_handler:
        importer = ImporterExtensionFactory.get_importer(
            pathlib.Path(input_file), file_handler
        )
        importer.import_file(pathlib.Path(input_file))

        exporter = ExporterExtensionFactory.get_exporter(
            pathlib.Path(output_path), file_handler
        )
        exporter.export_file(pathlib.Path(output_path), output_path)


if __name__ == "__main__":
    main()