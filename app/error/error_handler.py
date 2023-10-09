from error_code import ErrorCode

ERROR_CODE_MAP = {
    400: ErrorCode.INVALID_ARGUMENT,
    401: ErrorCode.UNAUTHENTICATED,
    403: ErrorCode.PERMISSION_DENIED,
    404: ErrorCode.NOT_FOUND,
    409: ErrorCode.ABORTED,
    429: ErrorCode.RESOURCE_EXHAUSTED,
    499: ErrorCode.CANCELLED,
    500: ErrorCode.INTERNAL,
    501: ErrorCode.NOT_IMPLEMENTED,
    502: ErrorCode.NETWORK_ERROR,
    503: ErrorCode.UNAVAILABLE,
    504: ErrorCode.DEADLINE_EXCEEDED,
}


def handle_error(error):
    """
    处理错误的函数，根据错误类型返回对应的错误代码和错误描述。
    """
    return ERROR_CODE_MAP.get(error.code, ErrorCode.UNKNOWN)
