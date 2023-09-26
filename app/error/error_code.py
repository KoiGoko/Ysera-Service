from enum import Enum


class ErrorCode(Enum):
    SUCCESS = 0
    INVALID_INPUT = 1
    FILE_NOT_FOUND = 2
    PERMISSION_DENIED = 3
    DATABASE_ERROR = 4
    NETWORK_ERROR = 5
    INTERNAL_ERROR = 6
