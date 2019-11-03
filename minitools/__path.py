import os

__all__ = ('get_current_path', 'to_path')


def get_current_path(file=__file__):
    return os.path.dirname(os.path.abspath(file))


def to_path(*args):
    return (os.sep).join(args)


if __name__ == '__main__':
    print(get_current_path())
    print(to_path(get_current_path(), 'czaOrz', 'test'))
