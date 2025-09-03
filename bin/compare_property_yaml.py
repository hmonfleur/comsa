#!/usr/bin/env python3
import argparse
import copy
import deepdiff
import yaml
import pprint
import os
import pdb

def diff_lists(base_list, diff_list):
    return { "added": list( set( [str(x) for x in diff_list] ).difference(set([str(x) for x in base_list]) )), 
             "removed": list( set( [str(x) for x in base_list]).difference(set([str(x) for x in diff_list]))) }

def diff_list_in_dicts(listpath, base_dict, diff_dict):
    try:
        l1 = get_dict_value_from_listpath(listpath, base_dict)
    except KeyError:
        l1 = []
    try:
        l2 = get_dict_value_from_listpath(listpath, diff_dict)
    except KeyError:
        l2 = []
    return diff_lists(l1, l2)

def count_dict_leaf_values(d, count_list_len=True):
    n = 0
    for k in d.keys():
        if type(d[k]) == dict:
            n += count_dict_leaf_values(d[k])
        elif type(d[k]) == list:
            if count_list_len:
                n += len(d[k])
            else:
                n += 1
        else:
            n += 1
    return n



def remove_similar_listpath(listpath_set):
    s = set()
    for e in listpath_set:
        if str(e) not in s:
            s.add(str(e))
        else:
            listpath_set.remove(e)
    return listpath_set


def listpath_through_dict(listpath, d, value_to_insert = None):
    if len(d) == 0 or len(listpath) == 0:
        return d
    for e in listpath[:-1]:
        if e not in d.keys():
            d[e] = {}
        d = d[e]
    if value_to_insert != None:
        d[listpath[-1]] = value_to_insert
    else:
        d[listpath[-1]] = {}
        d = d[listpath[-1]]
    return d

def get_dict_path_as_list_from_deepdiff_dict_item(dictdiff_item):
    res = dictdiff_item.replace('root', "").replace("[", "").replace("'", "").split("]")
    res.remove("")
    return res

def get_dict_value_from_listpath(listpath, d):
    for e in listpath:
        try:
            d = d[e]
        except TypeError as err:
            if type(d) == type([]):
                d = d[int(e)]
    return d

def yaml_diff_dict(base_dict, compared_to_dict, deepdiff_dict):
    list_to_check = []
    result_dict = {}
    result_dict['ADDED'] = {}
    result_dict['REMOVED'] = {}
    result_dict['MODIFIED'] = {}
    result_dict['TYPE_CHANGES'] = {}
    if 'dictionary_item_added' in deepdiff_dict.keys():
        for item in deepdiff_dict['dictionary_item_added']:
            tmp_dict = result_dict['ADDED']
            listpath = get_dict_path_as_list_from_deepdiff_dict_item(item)
            value = get_dict_value_from_listpath(listpath, compared_to_dict)
            if (type(value) == list):
                list_to_check.append(listpath)
            else:
                tmp_dict = listpath_through_dict(listpath[0:-1], tmp_dict)
                tmp_dict[listpath[-1]] = value
    if 'dictionary_item_removed' in deepdiff_dict.keys():
        for item in deepdiff_dict['dictionary_item_removed']:
            listpath = get_dict_path_as_list_from_deepdiff_dict_item(item)
            value = get_dict_value_from_listpath(listpath, base_dict)
            if (type(value) == list):
                list_to_check.append(listpath)
            else:
                tmp_dict = result_dict['REMOVED']
                tmp_dict = listpath_through_dict(listpath[0:-1], tmp_dict)
                tmp_dict[listpath[-1]] = value
    if 'iterable_item_added' in deepdiff_dict.keys():
        for key in deepdiff_dict['iterable_item_added'].keys():
            value = deepdiff_dict['iterable_item_added'][key]
            listpath = get_dict_path_as_list_from_deepdiff_dict_item(key)
            list_to_check.append(listpath[:-1])
            #tmp_dict = result_dict['ADDED']
            #tmp_dict = listpath_through_dict(listpath[0:-2], tmp_dict)
            #if listpath[-2] not in tmp_dict.keys():
            #    tmp_dict[listpath[-2]] = []
            #tmp_dict[listpath[-2]].append(value)
    if 'iterable_item_removed' in deepdiff_dict.keys():
        for key in deepdiff_dict['iterable_item_removed'].keys():
            value = deepdiff_dict['iterable_item_removed'][key]
            listpath = get_dict_path_as_list_from_deepdiff_dict_item(key)
            list_to_check.append(listpath[:-1])
            #tmp_dict = result_dict['REMOVED']
            #tmp_dict = listpath_through_dict(listpath[0:-2], tmp_dict)
            #if listpath[-2] not in tmp_dict.keys():
            #    tmp_dict[listpath[-2]] = []
            #tmp_dict[listpath[-2]].append(value)
    if 'values_changed' in deepdiff_dict.keys():
        for key in deepdiff_dict['values_changed']:
            listpath = get_dict_path_as_list_from_deepdiff_dict_item(key)
            if type(get_dict_value_from_listpath(listpath[:-1], base_dict)) == list:
                list_to_check.append(listpath[:-1])
                #if listpath[-2] not in tmp_dict.keys():
                #    tmp_dict[listpath[-2]] = []
                #tmp_dict[listpath[-2]].append(deepdiff_dict['values_changed'][key])
            else:
                tmp_dict = result_dict['MODIFIED']
                tmp_dict = listpath_through_dict(listpath[0:-2], tmp_dict)
                if len(listpath) == 1:
                    if listpath[0] not in tmp_dict.keys():
                        tmp_dict[listpath[0]] = {}
                    tmp_dict[listpath[0]] = deepdiff_dict['values_changed'][key]
                else:
                    if listpath[-2] not in tmp_dict.keys():
                        tmp_dict[listpath[-2]] = {}
                    tmp_dict[listpath[-2]][listpath[-1]] = deepdiff_dict['values_changed'][key]
    if 'type_changes' in deepdiff_dict.keys():
        for key in deepdiff_dict['type_changes']:
            listpath = get_dict_path_as_list_from_deepdiff_dict_item(key)
            if type(get_dict_value_from_listpath(listpath[:-1], base_dict)) == list:
                list_to_check.append(listpath[:-1])
#                if listpath[-2] not in tmp_dict.keys():
#                    tmp_dict[listpath[-2]] = []
#                tmp_dict[listpath[-2]].append(deepdiff_dict['type_changes'][key])
#                del tmp_dict[listpath[-2]][-1]["new_type"]
#                del tmp_dict[listpath[-2]][-1]["old_type"]
            else:
                old_value_str = str(deepdiff_dict['type_changes'][key]['old_value'])
                new_value_str = str(deepdiff_dict['type_changes'][key]['new_value'])
                if old_value_str != new_value_str :
                    tmp_dict = result_dict['MODIFIED']
                else:
                    uncounted_type_changes += 1
                    tmp_dict = result_dict['TYPE_CHANGES']
                tmp_dict = listpath_through_dict(listpath[0:-2], tmp_dict)

                if len(listpath) == 1:
                    if listpath[0] not in tmp_dict.keys():
                        tmp_dict[listpath[0]] = {}
                    tmp_dict[listpath[0]] = deepdiff_dict['type_changes'][key]
                    del tmp_dict[listpath[0]]["new_type"]
                    del tmp_dict[listpath[0]]["old_type"]
                else:
                    if listpath[-2] not in tmp_dict.keys():
                        tmp_dict[listpath[-2]] = {}
                    tmp_dict[listpath[-2]][listpath[-1]] = deepdiff_dict['type_changes'][key]
                    del tmp_dict[listpath[-2]][listpath[-1]]["new_type"]
                    del tmp_dict[listpath[-2]][listpath[-1]]["old_type"]


    for listpath in remove_similar_listpath(list_to_check):
        listpath_difference = diff_list_in_dicts(listpath, base_dict, compared_to_dict)
        if listpath_difference["added"] != []:
            listpath_through_dict(listpath, result_dict["ADDED"], value_to_insert=listpath_difference["added"])
        if listpath_difference["removed"] != []:
            listpath_through_dict(listpath, result_dict["REMOVED"], value_to_insert=listpath_difference["removed"])


    result_dict["metadata"] = {"differences": {"TOTAL": 0, 
                                "additions": count_dict_leaf_values(result_dict["ADDED"]), 
                                "removals": count_dict_leaf_values(result_dict["REMOVED"]), 
                                "modifications": count_dict_leaf_values(result_dict["MODIFIED"]) 
                                }}

    result_dict["metadata"]["differences"]["TOTAL"] = result_dict["metadata"]["differences"]["additions"] + result_dict["metadata"]["differences"]["removals"] + result_dict["metadata"]["differences"]["modifications"] 
    return result_dict




def main():

    DEFAULT_FOLDER = "./yaml_diff_output"

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("yaml1_filepath")
    argument_parser.add_argument("yaml2_filepath")
    argument_parser.add_argument("-o", "--outfile", nargs='?', const="default", default=None)
    argument_parser.add_argument("--data-type", default="docker-compose")
    args = vars(argument_parser.parse_args())
    
    
    diff_dict = {}
    with open(args["yaml1_filepath"], "r") as f1:
        d1 = yaml.safe_load(f1)

    with open(args["yaml2_filepath"], "r") as f2:
        d2 = yaml.safe_load(f2)

    if args["data_type"] == "docker-compose":
        if "services" not in d1.keys():
            d1 = {"services":d1}

        if "services" not in d2.keys():
            d2 = {"services":d2}

    diff_dict = deepdiff.DeepDiff(d1,d2)
    
    result_diff_dict = yaml_diff_dict(d1,d2,diff_dict)
    result_diff_dict["metadata"]["base_file"]=args["yaml1_filepath"]
    result_diff_dict["metadata"]["compared_to"]=args["yaml2_filepath"]
        
    if args["outfile"] != None:
        if args["outfile"] == "default":
            if not os.path.exists(DEFAULT_FOLDER):
                os.mkdir(DEFAULT_FOLDER)
            output_filename = ".".join(args["yaml1_filepath"].split("/")[-1].split(".")[0:-1]) + "_vs_" + ".".join(args["yaml2_filepath"].split("/")[-1].split(".")[0:-1]) + ".yaml"
            output_filepath = os.path.join(DEFAULT_FOLDER, output_filename)
            args["outfile"] = output_filepath
        
            
        with open(args["outfile"], "w") as f:
                yaml.dump(result_diff_dict, f)
        
        print("comparison file created at " + os.path.abspath(args["outfile"]) + "\n")
    
    return_code = int(result_diff_dict["metadata"]["differences"]["TOTAL"])
    print("Differences from {} to {}:".format(args["yaml1_filepath"], args["yaml2_filepath"]))
    pprint.pp(result_diff_dict["metadata"]["differences"])

    exit(return_code)

if __name__ == "__main__":
    main()
