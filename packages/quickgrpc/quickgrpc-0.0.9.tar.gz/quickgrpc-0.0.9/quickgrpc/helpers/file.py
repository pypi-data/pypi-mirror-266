import contextlib
import os
import shutil
from pathlib import Path


import logging

logger = logging.getLogger(__name__)


def read_file(path):
    with open(path, "r") as f:
        return f.read()


def write_file(file, data):
    """
    The write_file function takes two arguments:
        file - the name of the file to write to
        data - a string containing the data to be written

    :param file: Specify the file to be written to
    :param data: Write the data to a file
    :return: Nothing

    """
    with open(file, "w") as f:
        f.write(data)


def append_file(file, line, force=False):
    """
    The append_file function takes two arguments:
        1. file - the name of a file to append to
        2. line - the line of text that will be appended to the end of the file

    :param file: Specify the file to be appended
    :param line: Append a line to the file
    :param force: Append a line to the file, at the end... remove if exists
    :return: The line that was appended

    """
    with open(file, "r") as reader:
        content = reader.read()
        if force:
            content.replace(line, '')
        if line in reader.read():
            return
    with open(file, "a") as file:
        file.write(f"{line}\n")



def create_new_folder(path):
    delete_folder(path)
    Path(path).mkdir(exist_ok=True)


def delete_folder(path):
    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree(path)


def check_base_dir():
    """
    The check_base_dir function is used to ensure that the user is running this script from within their project directory.
    This function will raise a RuntimeError if it does not find a main.py file in the current working directory.

    :return: A runtimeerror if the current directory does not contain a main

    """
    if not os.path.exists("manage.py"):
        raise RuntimeError(
            'Make sure to run this within your project directory. Use "create_project" to create a new one if needed'
        )


def copy_if_exists(src, dest):
    try:
        shutil.copy(src, dest)
    except FileNotFoundError:
        logger.warning(f"{src} is missing, skipping")
