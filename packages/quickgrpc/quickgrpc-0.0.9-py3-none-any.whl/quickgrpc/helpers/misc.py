import importlib
import os
import site
import sysconfig
from pathlib import Path

import black
import isort

from quickgrpc.helpers.file import write_file


def create_package(name):
    """
    The create_package function creates a directory with the name of the package, and then
    creates an empty __init__.py file in that directory.

    :param name: Create a directory with the same name
    :return: A path object

    """
    Path(name).mkdir(exist_ok=True, parents=True)
    write_file(f"{name}/__init__.py", "")


def format_with_black(folder_path):
    # Walk through the directory tree
    """
    The format_folder function takes a folder path as an argument and recursively
    walks through the directory tree, formatting all Python files it finds using Black.


    :param folder_path: Specify the folder to format
    :return: Nothing

    """
    for root, dirs, files in os.walk(folder_path):
        # Iterate over the files in the current directory
        for file_name in files:
            # Check if the file is a Python file
            if file_name.endswith(".py"):
                # Get the full path to the file
                file_path = os.path.join(root, file_name)
                # Format the file using Black
                with open(file_path, "r") as file:
                    code = file.read()
                formatted_code = black.format_str(code, mode=black.FileMode())
                with open(file_path, "w") as file:
                    file.write(formatted_code)
            # If the file is a directory, recursively call the function
            elif os.path.isdir(os.path.join(root, file_name)):
                format_with_black(os.path.join(root, file_name))


def check_library_installation(library_name):
    try:
        importlib.import_module(library_name)
    except ImportError as e:
        raise ImportError(f"The library '{library_name}' is not installed.") from e


def install_library(library_name, token, version=None):
    from pip._internal import main as pip_main

    pkg = f"git+https://{token}@github.com/BankBuddy/bud-core-{library_name}-lib"
    if version:
        pkg += f"@{version}"
    pip_main(["install", pkg])


def prepend(l, x):
    """
    The prepend function takes a list and an element as arguments.
    It checks if the element is in the list, and if it isn't, it inserts
    the element at index 0 of the list.

    :param l: Specify the list that we want to add an item to
    :param x: Specify the value that is being inserted into the list
    :return: None

    """
    if x not in l:
        l.insert(0, x)


def get_python_lib():
    """
    The get_python_lib function returns the path to the site-packages directory for
    the current Python installation. This is useful when you need to install a package
    that contains data files that are needed by other modules, but you don’t want to
    hardcode paths into your module. For example, if your module needs some data files in /usr/local/share/mymodule/, and these files are not part of the source distribution (i.e., they are installed separately), then you can use this function as follows:

    :return: The path to the site-packages directory

    """
    path = sysconfig.get_path("purelib") or site.getsitepackages()[0]
    return path if os.path.exists(path) else "/usr/local/lib/python3.9/site-packages"


def sort_imports(file_path):
    # Load the content of the file
    with open(file_path, "r") as f:
        file_content = f.read()

    # Apply import sorting
    sorted_content = isort.code(file_content, float_to_top=True)

    # Write the sorted content back to the file
    with open(file_path, "w") as f:
        f.write(sorted_content.replace("\n\nfrom", "\nfrom"))
