import os
import shutil


def rm_pycache(path: str=None, stdout: bool=False) -> None or Exception:
    """
    Delete all __pycache__ directories in the specified path.

    :param path: path to directory to search for __pycache__
    :type path: str
    :default path: current working directory

    :param stdout: print output to stdout
    :type stdout: bool
    :default stdout: False

    :return: None | Exception

    >>> rm_pycache(path='./src', stdout=True)
    """

    if path is None:
        path = os.getcwd()

    try:
        count = 0

        for directory, subfolder, file in os.walk(path):
            if os.path.isdir(directory):
                if directory[::-1][:11][::-1] == '__pycache__':
                    shutil.rmtree(directory)
                    count += 1

        stdout and print(f' * Destroyed ({count}) __pycache__ directories')

    except Exception as exc:
        print('rm_pycache() Error:\n', exc)
