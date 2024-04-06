# -*- coding: utf-8 -*-
import filecmp
import os
import re

import json5
import yaml


def get_json_field(field, string):
    match = re.search(rf'"{field}":\s*', string)
    if match:
        start = match.span()[0]
        dstr = string[start:]
        s = 0
        end = start+1
        for i, c in enumerate(dstr):
            if c == '{':
                s += 1
            elif c == '}':
                s -= 1
                if s == 0:
                    end = i+1
                    break
    data = json5.loads("{" + dstr[:end] + "}")
    return data.get(field)


def yaml_loader():
    """Custom YAML loader."""
    pattern = re.compile('.*?\${(\w+)}.*?')
    loader = yaml.SafeLoader
    tag = '!ENV'
    loader.add_implicit_resolver(tag, pattern, None)

    def constructor_env_variables(loader, node):
        """
        Extracts the environment variable from the node's value
        :param yaml.Loader loader: the yaml loader
        :param node: the current node in the yaml
        :return: the parsed string that contains the value of the environment
        variable
        """
        value = loader.construct_scalar(node)
        match = pattern.findall(value)  # to find all env variables in line
        if match:
            full_value = value
            for g in match:
                full_value = full_value.replace(
                    f'${{{g}}}', os.environ.get(g, g)
                )
            return full_value
        return value

    loader.add_constructor(tag, constructor_env_variables)
    return loader


def read_yaml(filepath):
    """Open and read YAML file and return a dictionary representation.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath)

    with open(filepath, "r", encoding="utf-8") as stream:
        ymldic = yaml.load(stream, Loader=yaml_loader())
        return ymldic


def compare_directories(left, right):
    """Return -1 if left dir is newer than right, or 1, or 0.
    This will compare each file to find the directory with newest file.
    Using mtime and cmp.
    """
    compared = 0
    compared_left = -1000
    compared_right = -1000
    left_files = []
    right_files = []
    right_diff_files = []

    for left_file in os.listdir(left):
        left_files.append(
            (left_file, os.path.getmtime(left + os.sep + left_file)))

    for right_file in os.listdir(right):
        if right_file not in [f[0] for f in left_files]:
            right_diff_files.append(
                (right_file, os.path.getmtime(right + os.sep + right_file)))
        else:
            right_files.append(
                (right_file, os.path.getmtime(right + os.sep + right_file)))

    if len(right_diff_files) > 0:
        compared = -1

    elif len(left_files) > len(right_files):
        compared = 1

    else:
        compared_left = 0
        compared_right = 0

        for right_set in right_files:
            left_set = [f for f in left_files if f[0] == right_set[0]][0]

            left_file = left + os.sep + left_set[0]
            right_file = right + os.sep + right_set[0]

            # If there's a renaming, exclude the field from comparison.
            if left_file[-3:] == ".yy" and right_file[-3:] == ".yy":
                if not filecmp.cmp(left_file, right_file):
                    with open(left_file, "r", encoding="utf-8") as f:
                        ljson = json5.load(f)
                        del ljson["parent"]
                    with open(right_file, "r", encoding="utf-8") as f:
                        rjson = json5.load(f)
                        del rjson["parent"]
                    if ljson == rjson:
                        continue

            if filecmp.cmp(left_file, right_file):
                continue
            compared_left = max(left_set[1], compared_left)
            compared_right = max(right_set[1], compared_right)
            compared = True

    if compared is not None:
        if compared_left > compared_right:
            compared = 1
        if compared_left < compared_right:
            compared = -1
        if compared_left == compared_right:
            compared = 0
    else:
        compared = 0

    return -1 if compared < 0 else 1 if compared > 0 else 0
