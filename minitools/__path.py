import os
import time
import shutil
import weakref
import collections

from .__logging import show_dynamic_ratio

__all__ = ('get_current_path', 'to_path', 'current_file_path', 'path2module',
           'find_file_by_name', 'modify_file_content', 'delete_file_by_name',
           'remove_file', 'remove_folder', 'rename_file')


def get_current_path(file=__file__):
    return os.path.dirname(os.path.abspath(file))


def to_path(*args):
    return (os.sep).join(args)


def current_file_path(filename, filepath):
    return to_path(get_current_path(filepath), filename)


def path2module(path):
    return '.'.join(path.split(os.sep))


def remove_file(filePath):
    os.remove(filePath)


def remove_folder(folderPath):
    shutil.rmtree(folderPath)


def rename_file(old, new):
    os.rename(old, new)


def find_file_by_name(filename='', folder='', path='.', findFolder=False):
    path_set = set()
    results = []

    def _walk_path(path):
        for currentPath, _, files in os.walk(path):
            if currentPath in path_set:
                continue
            path_set.add(currentPath)
            if not findFolder and currentPath.endswith(folder) and filename in files:
                results.append(to_path(currentPath, filename))
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


class MiniCache:  # todo， 参考scrapy的弱引用，应该可以学到不少
    notFound = object()

    class Dict(dict):
        def __del__(self):
            pass

    def __init__(self, maxLen=10):
        self.weak = weakref.WeakValueDictionary()
        self.strong = collections.deque(maxlen=maxLen)

    @staticmethod
    def getNowTime():
        return int(time.time())

    def get(self, key):
        temp = self.weak.copy()
        for key, value in temp.items():
            if self.getNowTime() > value[r'expire']:
                self.weak.pop(key)
        value = self.weak.get(key, self.notFound)
        if value is self.notFound or self.getNowTime() > value[r'expire']:
            return self.notFound
        return value

    def set(self, key, value):
        self.weak[key] = strongRef = MiniCache.Dict(value)
        self.strong.append(strongRef)
