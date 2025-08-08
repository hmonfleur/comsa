from argparse import ArgumentParser
import subprocess as sp
import os
import sys

executable_list = [
"compose2diagram",
"compose2k8s",
"compose2yaml",
"compose-check",
"compose-metrics",
"comsa2compose",
"comsa2compose-yaml",
"comsa2k8s",
"comsa2yaml",
"comsa-analysis",
"comsa-check",
"comsa-metrics",
"comsa-scattering",
"comsa-tangling",
"comsa-type-scattering",
"hypercomsa"
]

# COMMAND LINE ARGUMENT PARSER
argument_parser = ArgumentParser(
        prog = 'COMSA toolbox',
        description = 'Toolbox for the Concern Oriented MicroService Architecture language.')

argument_parser.add_argument("-o", default=False, type=str, help="Output file, stdout if not set")
argument_parser.add_argument("--executables_folder_path", default="./bin/", type=str, help="Executables folder path")
argument_parser.add_argument("executable", choices=executable_list, help="Select a tool among {}".format((", ").join(executable_list)))
argument_parser.add_argument("input_file", help="Input file")
args = vars(argument_parser.parse_args())

os.environ['PATH'] += os.pathsep + args["executables_folder_path"]

if args["executable"] == "hypercomsa":
    ret = sp.run([os.path.join(args["executables_folder_path"], args["executable"]), args["input_file"], args['o']], capture_output=True, text=True)
    exit(ret.returncode)


ret = sp.run([os.path.join(args["executables_folder_path"], args["executable"]), args["input_file"]], capture_output=True, text=True)

if ret.returncode != 0:
    print(ret.stderr, file=sys.stderr)
    exit(ret.returncode)

if args["o"]:
    with open(args["o"], "w") as f:
        print(ret.stdout, file=f)
        exit(0)

print(ret.stdout, file=sys.stdout)
exit(0)
