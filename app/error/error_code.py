from enum import Enum


class ErrorCode(Enum):
    """
    Enum class defining Google API error codes along with corresponding descriptions and comments.
    """

    INVALID_ARGUMENT = (400, "客户端指定了无效参数。如需了解详情，请查看错误消息和错误详细信息。")
    FAILED_PRECONDITION = (400, "请求无法在当前系统状态下执行，例如删除非空目录。")
    OUT_OF_RANGE = (400, "客户端指定了无效范围。")
    UNAUTHENTICATED = (401, "由于 OAuth 令牌丢失、无效或过期，请求未通过身份验证。")
    PERMISSION_DENIED = (403, "客户端权限不足。这可能是因为 OAuth 令牌没有正确的范围、客户端没有权限或者 API 尚未启用。")
    NOT_FOUND = (404, "未找到指定的资源。")
    ABORTED = (409, "并发冲突，例如读取/修改/写入冲突。")
    ALREADY_EXISTS = (409, "客户端尝试创建的资源已存在。")
    RESOURCE_EXHAUSTED = (
    429, "资源配额不足或达到速率限制。如需了解详情，客户端应该查找 google.rpc.QuotaFailure 错误详细信息。")
    CANCELLED = (499, "请求被客户端取消。")
    DATA_LOSS = (500, "出现不可恢复的数据丢失或数据损坏。客户端应该向用户报告错误。")
    UNKNOWN = (500, "出现未知的服务器错误。通常是服务器错误。")
    INTERNAL = (500, "出现内部服务器错误。通常是服务器错误。")
    NOT_IMPLEMENTED = (501, "API 方法未通过服务器实现。")
    NETWORK_ERROR = (502, "到达服务器前发生网络错误。通常是网络中断或配置错误。")
    UNAVAILABLE = (503, "服务不可用。通常是服务器已关闭。")
    DEADLINE_EXCEEDED = (504,
                         "超出请求时限。仅当调用者设置的时限比方法的默认时限短（即请求的时限不足以让服务器处理请求）并且请求未在时限范围内完成时，才会发生这种情况。")

    def __init__(self, code: int, message: str):
        self.code: int = code
        self.message: str = message

    def __str__(self) -> str:
        """
        Override __str__ method for easy printing of ErrorCode objects.
        """
        return f"ErrorCode: code = {self.code}, message = {self.message}"

    def __doc__(self) -> str:
        """
        Provide docstring for each ErrorCode member.
        """
        return f"Error code: {self.code}\nDescription: {self.message}"
