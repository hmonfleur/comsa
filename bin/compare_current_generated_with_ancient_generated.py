#!/usr/bin/env python3
import argparse
import subprocess
from sys import stdout
import deepdiff
import yaml
import pprint
import os
import re
import pdb

DEFAULT_COMPARISON_DIR = "/tmp/comsa4compose_compare"
DEFAULT_FOLDER_TO_COMPARE = "generated/"
DEFAULT_EXTENSIONS_TO_COMPARE = {"yml": "^.*\.yml$(?<!\.k8s\.yml)$", "k8s.yml": "^.*\.k8s\.yml"}
#DEFAULT_EXTENSIONS_TO_COMPARE = ["^.*\.k8s\.yml", "^.*\.yml$(?<!\.k8s\.yml)$"]

FOLDERS_CURRENT_PRECEDENT = ["current", "precedent"]

def compare_folders_files(folder1, folder2):
    f1_files = set(os.listdir(folder1))
    f2_files = set(os.listdir(folder2))
    return(f1_files.intersection(f2_files), f1_files.difference(f2_files), f2_files.difference(f1_files))


def get_matching_files(folder_path, regex_pattern):
    # Compile the regex pattern
    pattern = re.compile(regex_pattern)
    
    # List to store matching file paths
    matching_files = []
    
    # Walk through the directory
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Check if the file name matches the regex pattern
            if pattern.match(file):
                # Add the full file path to the list
                matching_files.append(os.path.join(root, file))
    
    return matching_files

def split_k8s_yaml_fileset(fileset, output_directory):
    print("Splitting {} k8s files into separate yaml ressources files.".format(len(fileset)))
    number_of_files_created = 0
    for f in fileset:
        number_of_files_created += split_k8s_yaml(f, output_directory)
    print(f"\033[K" + "DONE: Produced {} files.".format(number_of_files_created))


def split_k8s_yaml(input_file, output_directory):
    """
    Splits a multi-resource Kubernetes YAML file into separate YAML files.
    
    Parameters:
    input_file (str): Path to the input multi-resource YAML file.
    output_directory (str): Directory where the split YAML files will be saved.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(input_file, 'r') as file:
        # Load all documents in the YAML file (separated by "---")
        documents = list(yaml.safe_load_all(file))

    number_of_files_created = 0

    for index, document in enumerate(documents, start=1):
        # Extract the kind and metadata name (if exists) for better file naming
        kind = document.get('kind', f'resource{index}')
        metadata = document.get('metadata', {})
        name = metadata.get('name', f'resource{index}')

        # Create a filename based on resource kind and name
        output_filename = f"{kind.lower()}-{name}.yaml"
        output_path = os.path.join(output_directory, os.path.basename(input_file).split(".")[0] + "_" + output_filename)

        # Write each resource into its own file
        with open(output_path, 'w') as output_file:
            yaml.dump(document, output_file)

        number_of_files_created += 1

        print(f"\033[K" + f"Created: {output_path}"+ "\r", end="", flush=True)

    return number_of_files_created


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("commit")
    argument_parser.add_argument("-f", default=False)
    argument_parser.add_argument("--k8s", action="store_true")
    argument_parser.add_argument("--comparison-dir", default=None)
    argument_parser.add_argument("--folder-to-compare", default=DEFAULT_FOLDER_TO_COMPARE)
    argument_parser.add_argument("--comparison-extensions", default = DEFAULT_EXTENSIONS_TO_COMPARE)
    args = vars(argument_parser.parse_args())

    if args["comparison_dir"] == None:
        comparison_dir = DEFAULT_COMPARISON_DIR + "_" + str(args["commit"])
    else:
        comparison_dir = args["comparison_dir"]

    if not args["k8s"]:
        del args["comparison_extensions"]["k8s.yml"]

    try:
        
        k8s_common = []

        subprocess.run(["rm", "-r", "-f", comparison_dir])
##        extensions_folders = [os.path.join(comparison_dir, re.sub(r'[^a-zA-Z0-9]', '', k)) for k in args["comparison_extensions"]]
##        folders_to_create = [os.path.join(ef, cpf) for ef in extensions_folders for cpf in FOLDERS_CURRENT_PRECEDENT]
##
##        for folder in folders_to_create:
##            os.makedirs(folder)
        os.makedirs(comparison_dir)

        subprocess.run(["git", "archive", "--format=tar", "--prefix=/", "-o", os.path.join(comparison_dir, "tmp.tar"), args["commit"], args["folder_to_compare"]])
        subprocess.run(["tar", "-xf",  os.path.join(comparison_dir, "tmp.tar")], cwd=comparison_dir)

        extract_folder = os.path.join(comparison_dir, args["folder_to_compare"])

        current_files = {"only_in":{}}
        precedent_files = {"only_in":{}}

        created_folders_to_compare = {}

        for key,ext_regex in args["comparison_extensions"].items():
            #key = re.sub(r'[^a-zA-Z0-9]', '', ext_regex)
            current_files[key] = set(get_matching_files(args["folder_to_compare"], ext_regex))
            precedent_files[key] = set(get_matching_files(extract_folder, ext_regex))
            common_files = set([os.path.basename(f) for f in current_files[key]]).intersection(set([os.path.basename(f) for f in precedent_files[key]]))
            current_files["only_in"][key] = (set([f for f in current_files[key] if os.path.basename(f) not in common_files]))
            precedent_files["only_in"][key] = (set([f for f in precedent_files[key] if os.path.basename(f) not in common_files]))
            current_files[key] = current_files[key].difference(current_files["only_in"][key])
            precedent_files[key] = precedent_files[key].difference(precedent_files["only_in"][key])
            
            new_folders_to_compare = [os.path.join(comparison_dir, key, ef) for ef in FOLDERS_CURRENT_PRECEDENT]
            diff_folder = os.path.join(comparison_dir, key, "diff")
            os.makedirs(diff_folder)
            os.makedirs(new_folders_to_compare[0])
            os.makedirs(new_folders_to_compare[1])
            created_folders_to_compare[key] = new_folders_to_compare

            #Printing info about files

            print("Common {} files:".format(key))
            pprint.pprint(common_files)
            print("")

            if len(current_files["only_in"][key]) > 0:
                print("{} files only in current".format(key))
                pprint.pprint(current_files["only_in"][key])
                print("")

            if len(precedent_files["only_in"][key]) > 0:
                print("{} files only in {}".format(key, args["commit"][:5]))
                pprint.pprint(precedent_files["only_in"][key])
                print("")

            if "k8s" in key:
                split_k8s_yaml_fileset(current_files[key], new_folders_to_compare[0])
                split_k8s_yaml_fileset(precedent_files[key], new_folders_to_compare[1])
                common_files, splited_only_current, splited_only_precedent = compare_folders_files(new_folders_to_compare[0], new_folders_to_compare[1])

                print("")

                if len(splited_only_current) > 0:
                    print("k8s resources produced only for current files:")
                    pprint.pprint(splited_only_current)
                    print("")

                if len(splited_only_precedent) > 0:
                    print("k8s resources produced only for {} files:".format(args["commit"]))
                    pprint.pprint(splited_only_precedent)
                    print("")

            else:
                subprocess.run(["cp", *current_files[key], new_folders_to_compare[0]])
                subprocess.run(["cp", *precedent_files[key], new_folders_to_compare[1]])

            #Compare files

            print("Comparing {} files:".format(key))

            number_of_files = len(common_files)
            file_counter = 0
            difference_counter = 0
    
            for file in common_files:
                file_counter +=1
                print(f"\033[K" + file + " " * (70 - len(file)) + "({}/{})".format(file_counter, number_of_files) +  "\r", end="", flush=True)
                diff_file = os.path.join(diff_folder, "diff_"+file)
                ret = subprocess.run(["python3", "./bin/compare_property_yaml.py", os.path.join(new_folders_to_compare[1], file), os.path.join(new_folders_to_compare[0], file), "-o", diff_file], stdout=subprocess.DEVNULL)
                if ret.returncode != 0:
                      difference_counter += 1
                else:
                    os.remove(diff_file)

            print(f"\033[K" + "DONE: {}/{} different files".format(difference_counter, number_of_files))
            print("Diff folder: " + diff_folder)
            print("")





        #pprint.pprint(current_files)
        #pprint.pprint(precedent_files)

    except Exception as e:
        print(e)

    
    

if __name__ == "__main__":
    main()
