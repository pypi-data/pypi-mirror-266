from enum import IntEnum

from strenum import StrEnum


class Integer(IntEnum):
    NEG_ONE = -1
    ZERO = 0
    ONE = 1
    TWO = 2
    TEN = 10


class Index(IntEnum):
    ZERO = Integer.ZERO
    ONE = Integer.ONE
    LAST = Integer.NEG_ONE


class String(StrEnum):
    SPACE = ' '
    EMPTY = ''
    NEXT_LINE = '\n'
    TAB = '\t'
    FORWARD_SLASH = '/'
    UNDERSCORE = '_'
    PERIOD = '.'
    CARRIAGE_RETURN = '\r'
