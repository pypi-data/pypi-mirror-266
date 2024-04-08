from strenum import StrEnum


class FileIOMode(StrEnum):
    READ = 'r'
    WRITE = 'w'
    WRITE_BINARY = 'wb'
    APPEND = 'a'


ILLEGAL_DIRECTORY_CHARACTERS = r'[:*?<>"\'|]'
ILLEGAL_FILENAME_CHARACTERS = r'[/]'  # More characters will be added in future on case by case basis
