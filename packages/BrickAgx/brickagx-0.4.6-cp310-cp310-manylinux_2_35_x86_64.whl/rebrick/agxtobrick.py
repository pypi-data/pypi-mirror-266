#!/usr/bin/env python3
import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Action, SUPPRESS
import agx
import agxIO
import agxSDK
from rebrick import AgxToBrickMapper, __version__, set_log_level

init = agx.AutoInit()

class VersionAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(__version__)
        exit(0)


def parse_args():
    parser = ArgumentParser(description="Convert .agx files to .brick", formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("agxfile", help="the .agx file to load")
    parser.add_argument("--root-system-name", metavar="<root system name>", help="Override the name of the root system model")
    parser.add_argument("--export-folder", metavar="<export folder>", help="Where to write exported trimesh:es", default="./")
    parser.add_argument("--loglevel", choices=["trace", "debug", "info", "warn", "error", "critical", "off"], help="Set log level", default="info")
    parser.add_argument("--version", help="Show version", action=VersionAction, nargs=0, default=SUPPRESS)
    parser.add_argument("--realprecision", help="Set precision of generated real values", type=int, default=6)
    return parser.parse_known_args()


def run():
    args, _ = parse_args()
    set_log_level(args.loglevel)
    simulation = agxSDK.Simulation()
    assembly = agxSDK.AssemblyRef(agxSDK.Assembly())
    if args.root_system_name is not None:
        assembly.setName(args.root_system_name)
    agxIO.readFile(args.agxfile, simulation, assembly.get())

    # Export trimeshes relative to the current directory
    export_folder = args.export_folder if os.path.isabs(args.export_folder) else os.path.join(os.getcwd(), args.export_folder)
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)
    mapper = AgxToBrickMapper(export_folder, True, args.realprecision)

    output_file = os.path.basename(args.agxfile.replace(".agx", ".brick"))
    print("writing to", output_file)
    with open(output_file, "w", encoding="utf8") as file:
        file.writelines(mapper.assemblyToBrick(assembly))

if __name__ == '__main__':
    run()
