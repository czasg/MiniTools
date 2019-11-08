import os
import re
import sys
import codecs

from setuptools import setup, find_packages

"""
1、python setup check
2、python setup sdist
3、twine upload dist/__packages__-__version__.tar.gz
"""

if sys.version_info < (3, 5, 0):
    raise RuntimeError("minitools requires Python 3.5.0+")


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts), 'r', encoding='utf-8').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name='minitools',
    version=find_version('minitools', 'version.py'),
    description="This is a minitools for python",
    long_description="see https://github.com/CzaOrz/MiniTools",
    author='czaOrz',
    author_email='chenziangsg@163.com',
    url='https://github.com/CzaOrz/MiniTools',
    packages=find_packages(),
    install_requires=[
        'parsel>=1.5.0',
        'requests>=2.20.0',
        'selenium>=3.141.0',
        'PyExecJS>=1.5.1',
        'pillow>=6.0.0',
        'baidu-aip>=2.2.17.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
