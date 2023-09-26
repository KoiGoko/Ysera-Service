from error_code import ErrorCode


def handle_error(error):
    """
    处理错误的函数，根据错误类型返回对应的错误代码和错误描述。
    """
    if error.code == 400:
        return ErrorCode.INVALID_ARGUMENT
    elif error.code == 401:
        return ErrorCode.UNAUTHENTICATED
    elif error.code == 403:
        return ErrorCode.PERMISSION_DENIED
    elif error.code == 404:
        return ErrorCode.NOT_FOUND
    elif error.code == 409:
        return ErrorCode.ABORTED
    elif error.code == 429:
        return ErrorCode.RESOURCE_EXHAUSTED
    elif error.code == 499:
        return ErrorCode.CANCELLED
    elif error.code == 500:
        return ErrorCode.INTERNAL
    elif error.code == 501:
        return ErrorCode.NOT_IMPLEMENTED
    elif error.code == 502:
        return ErrorCode.NETWORK_ERROR
    elif error.code == 503:
        return ErrorCode.UNAVAILABLE
    elif error.code == 504:
        return ErrorCode.DEADLINE_EXCEEDED
    else:
        return ErrorCode.UNKNOWN
