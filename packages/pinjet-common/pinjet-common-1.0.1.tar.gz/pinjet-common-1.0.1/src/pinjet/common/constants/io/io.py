from typing import List

from strenum import StrEnum


class FileIOMode(StrEnum):
    READ = 'r'
    WRITE = 'w'
    WRITE_BINARY = 'wb'
    APPEND = 'a'


ILLEGAL_DIRECTORY_CHARACTERS = r'[:*?<>"\'|]'
ILLEGAL_FILENAME_CHARACTERS = r'[/]'  # More characters will be added in future on case by case basis

PYTHON_SCRIPT_EXTENSION: str = '.py'

SKIPPABLE_DIRECTORIES: List[str] = [
    'build',
    'bin',
    'lib',
    'Lib',
    'dist',
    'lib64',
    'share',
    'MACOSX',
    'Scripts',
    'include',
    'Include',
    '.egg-info',
    'pyvenv.cfg',
    '__pycache__',
]
