import os

__all__ = ('get_current_path', 'to_path', 'current_file_path', 'path2module')


def get_current_path(file=__file__):
    return os.path.dirname(os.path.abspath(file))


def to_path(*args):
    return (os.sep).join(args)


def current_file_path(filename, filepath):
    return to_path(get_current_path(filepath), filename)


def path2module(path):
    return '.'.join(path.split(os.sep))
