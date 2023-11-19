from pathlib import Path
import sys
from typing import List

PYTHON_PKG_DIST = "/usr/lib/python3/dist-packages"
REQ_PATTERN = "Requires-Dist:"

def read_req_file(path: str = "requirements.txt"):
    if Path(path).exists():
        content = open(path).read()    
    else:
        print("requirements.txt not found,\nPlease make sure the file exists.")
        sys.exit(1) 
    return content

def parse_metadata(path:str, pattern:str):
    pattern_list = []
    with open(path) as meta_file:
        while line := meta_file.readline():
            if line == "":
                break
            elif line.startswith(pattern):
                pattern_list.append(line.split(pattern)[1].split(";")[0].strip())
    return pattern_list


def get_dependencies(package:str):
    dependencies = []
    metadata_f_path = None
    search_glob_gen = Path(PYTHON_PKG_DIST).glob(f"{package.replace('-', '_')}*info")
    search_glob = [path for path in search_glob_gen if Path(path).exists()]
    if len(search_glob) > 0:
        if search_glob[0].is_dir():
            pkg_dir = search_glob[0]
            if Path(pkg_dir, "METADATA").exists():
                metadata_f_path = str(Path(pkg_dir, "METADATA"))
            elif Path(pkg_dir, "PKG-INFO").exists():
                metadata_f_path = str(Path(pkg_dir, "PKG-INFO"))
        elif search_glob[0].is_file():
            metadata_f_path = str(search_glob[0])
        if metadata_f_path is not None:
            dependencies = parse_metadata(metadata_f_path, REQ_PATTERN)

    return dependencies

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


def build_tree(deps_list: List):
    tree_dct = {"requirements.txt": []}
    for package, deps in deps_list:
        tree_dct["requirements.txt"].append(package)
        tree_dct[package] = deps
    return tree_dct


def main():
    reqs = read_req_file()
    packages = reqs.splitlines() 
    dependences_tree = []

    for package in packages:
        pkg_name = package.split("==")[0]
        pkg_deps = get_dependencies(pkg_name)
        dependences_tree.append([package, pkg_deps])

    tree_dct = build_tree(dependences_tree)
    ptree("requirements.txt", tree_dct)

if __name__ == "__main__":
    main()
