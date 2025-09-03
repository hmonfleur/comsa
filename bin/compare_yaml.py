#!/usr/bin/env python3
import argparse
from threading import settrace
import deepdiff
import yaml
from pprint import pprint
import pdb

argument_parser = argparse.ArgumentParser()
argument_parser.add_argument("yaml1_filepath")
argument_parser.add_argument("yaml2_filepath")
argument_parser.add_argument("--pdb", action="store_true")
args = vars(argument_parser.parse_args())


diff_dict = {}
with open(args["yaml1_filepath"], "r") as f1:
    with open(args["yaml2_filepath"], "r") as f2:
        d1 = yaml.safe_load(f1)
        d2 = yaml.safe_load(f2)
        diff_dict = deepdiff.DeepDiff(d1,d2, ignore_order=True)

if args["pdb"]:
    pdb.set_trace(header=str(len(diff_dict)))

if len(diff_dict) == 0:
    print("Files are equivalent (ignored order of iterables)")
else:
    print("Files are NOT equivalent (ignored order of iterables)")

exit(len(diff_dict))
