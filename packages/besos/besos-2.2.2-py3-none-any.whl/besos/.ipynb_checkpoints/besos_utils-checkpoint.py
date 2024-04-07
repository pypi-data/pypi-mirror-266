""" Helper functions to be used throughout the code base """


def listify(arg) -> list:
    """Converts the argument to a list if possible.
    If it is not iterable (i.e. one item), wrap it in a list.
    Treat strings as 1 item.
    :param arg: item(s) to be wrapped in list
    :return: List of the file arg(s)"""
    if isinstance(arg, str):
        return [arg]
    try:
        return list(arg)
    except TypeError:
        return [arg]


def get_file_name(path):
    """Finds and returns the file name from the path

    :param path: A directory to the idf file
    :return: String of file name
    """
    path = str(path).replace("\\", "/")
    if path.endswith("/"):
        path = path[:-2]
    file_name = path.split("/")[-1]
    return file_name
