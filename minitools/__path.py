import os
import re
import time
import string
import shutil

from functools import wraps

from .__logging import show_dynamic_ratio

__all__ = ('get_current_path', 'to_path', 'current_file_path', 'path2module',
           'find_file_by_name', 'modify_file_content', 'delete_file_by_name',
           'remove_file', 'remove_folder', 'rename_file', 'MiniCache',
           'check_logger_files', 'make_dir', 'make_file', 'create_template')


def get_current_path(file=__file__):
    return os.path.dirname(os.path.abspath(file))


def to_path(*args, sep=os.sep, forceStr=False, split=None):
    if forceStr:
        args = [str(arg) for arg in args]
    if split:
        new_args = []
        start = None
        for spl in split:
            index = spl.pop('index')
            new_args.append(to_path(*args[start:index], **spl))
            start = index
        args[:] = new_args
    return (sep).join(args)


def current_file_path(filename, filepath):
    return to_path(get_current_path(filepath), filename)


def path2module(path):
    return '.'.join(filter(lambda x: x, re.split(r'[/\\]|\.py', path)))


def make_dir(path, mode=0o777, exist_ok=True):
    os.makedirs(path, mode, exist_ok=exist_ok)


def make_file(file, content=''):
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)


def remove_file(filePath):
    os.remove(filePath)


def remove_folder(folderPath):
    shutil.rmtree(folderPath)


def rename_file(old, new):
    os.rename(old, new)


def create_template(path, template, config):
    text = string.Template(template).substitute(**config).lstrip()
    make_file(path, text)


def find_file_by_name(filename='', folder='', path='.', findFolder=False, matching=None):
    path_set = set()
    results = []

    def _walk_path(path):
        for currentPath, _, files in os.walk(path):
            if currentPath in path_set:
                continue
            path_set.add(currentPath)
            if not findFolder and currentPath.endswith(folder):
                if filename in files:
                    results.append(to_path(currentPath, filename))
                elif matching:
                    for file in files:
                        if getattr(file, matching)(filename):
                            results.append(to_path(currentPath, file))
            elif findFolder and currentPath.endswith(folder):
                results.append(currentPath)
            else:
                _walk_path(currentPath)

    _walk_path(path)
    return results


def delete_file_by_name(filename='', folder='', path='.', deleteFolder=False):
    files = find_file_by_name(filename, folder, path, findFolder=deleteFolder)
    remove_func = remove_folder if deleteFolder else remove_file
    count = len(files)
    cur = 0
    for file in files:
        remove_func(file)
        cur += 1
        show_dynamic_ratio(cur, count, text='delete rate')


def modify_file_content(string, replace='', filename='', folder='', path='.'):
    files = find_file_by_name(filename, folder, path)
    count = 0
    for file in files:
        temp_file = file + '.temp'
        with open(file, 'r', encoding='utf-8') as f_r, \
                open(temp_file, 'w', encoding='utf-8') as f_w:
            line_data = f_r.read(8096)
            while line_data:
                if string in line_data:
                    count += 1
                    line_data = line_data.replace(string, replace)
                f_w.write(line_data)
                line_data = f_r.read(8096)
        remove_file(file)
        rename_file(temp_file, file)
    print("Modify Success!")
    print("{} -> {}".format(string, replace))
    print("file count: {}".format(len(files)))
    print("modify count: {}".format(count))


def check_logger_files(name, path='.', spl='._', expires=60 * 60 * 24 * 3):
    LOGFER_FILE_SPLIT = re.compile(f'[{spl}]').split
    for currentPath, folders, files in os.walk(path):
        for file in files:
            if file.startswith(name):
                logName, logTime = LOGFER_FILE_SPLIT(file)[:2]
                if (int(time.time()) - int(logTime)) > expires:
                    remove_file(to_path(currentPath, file))
        break


class MiniCache:
    notFound = object()
    instance_cache = None

    class Dict(dict):
        def __del__(self):
            pass

    def __init__(self):
        self.weak = dict()  # todo, change this to weakref?

    @staticmethod
    def getNowTime():
        return int(time.time())

    def get(self, key):
        temp = self.weak.copy()
        for di_key, di_value in temp.items():
            if self.getNowTime() > di_value[r'expire']:
                self.weak.pop(di_key)
        value = self.weak.get(key, self.notFound)
        if value is self.notFound or self.getNowTime() > value[r'expire']:
            return self.notFound
        return value

    def set(self, key, value):
        self.weak[key] = MiniCache.Dict(value)

    def miniCache(self, expire=60 * 60 * 12):
        def wrapper(func):
            @wraps(func)
            def _wrapper(*args, **kwargs):
                key = self.get_keys(func, *args, **kwargs)
                result = self.get(key)
                if result is self.notFound:
                    result = func(*args, **kwargs)
                    self.set(key, {r'result': result, r'expire': expire + self.getNowTime()})
                    return result
                else:
                    result = result[r'result']
                    return result

            return _wrapper

        return wrapper

    def get_keys(self, func, *args, **kwargs):
        return func.__name__

    @classmethod
    def get_instance(cls):
        if not cls.instance_cache:
            cls.instance_cache = cls()
        return cls.instance_cache
