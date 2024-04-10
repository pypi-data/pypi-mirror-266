import os
from json import load as json_load


def join_cwd(*args) -> str:
    return os.path.normpath(os.path.join(os.getcwd(), *args))


def join(*args) -> str:
    return os.path.normpath(os.path.join(*args))


def exists_or_error(file_path: str) -> None:
    """ Raise Exception if File Path does not exist

    Args:
        file_path (str): an input path

    Raises:
        FileNotFoundError: an input path
    """
    if not exists(file_path):
        raise FileNotFoundError(file_path)


def exists(file_path: str) -> bool:
    """ Check if File or Directory exists

    Args:
        file_path (str): a file path

    Returns:
        bool: True if file or directory exists
    """
    return os.path.exists(file_path)


def read_json(file_path: str) -> object:
    """ Read JSON from File

    Args:
        file_path (str): the absolute and qualified output file path
        file_encoding (str, optional): The output file encoding. Defaults to "utf-8".

    Returns:
        [type]: the JSON object
    """
    with open(file_path) as json_file:
        return json_load(json_file)
