#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys
from importlib.metadata import requires


def ptree(start, tree, indent_width=4):

    def _ptree(start, parent, tree, grandpa=None, indent=""):
        if parent != start:
            if grandpa is None:
                print(parent, end="")
            else:
                print(parent)
        if parent not in tree:
            return
        for child in tree[parent][:-1]:
            print(indent + "├" + "─" * indent_width, end="")
            _ptree(start, child, tree, parent, indent + "│" + " " * 4)
        if len(tree[parent]) > 0:
            child = tree[parent][-1]
            print(indent + "└" + "─" * indent_width, end="")
            _ptree(start, child, tree, parent, indent + " " * 5)  # 4 -> 5

    parent = start
    print(start)
    _ptree(start, parent, tree)

def get_dependencies(package_name):
    deps = requires(package_name)
    if deps is None:
        deps = ""
    return deps

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("requirements_file")
    args = parser.parse_args()

    req_file = args.requirements_file
    if not Path(req_file).exists():
        print(f"No {req_file} found.")
        sys.exit(0)
    
    if sys.prefix == sys.base_prefix:
        print("You are not inside any virtual environment")
        sys.exit(1)
    venv = str(Path(sys.prefix).name)

    packages = []
    with open(req_file) as file:
        tmp = file.readlines()

    for package in tmp:
        name = package.split("==")[0]
        deps = get_dependencies(name)
        packages.append((package, deps))

    tree_dct = {venv: []}
    for package , deps in packages:
        tree_dct[venv].append(package)
        tree_dct[package] = deps

    ptree(venv, tree_dct)
