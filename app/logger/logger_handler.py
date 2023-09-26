from logger_code import ErrorCode


def process_data(data):
    # process data here
    if not data:
        return ErrorCode.INVALID_INPUT, None

    # process data here
    return ErrorCode.SUCCESS, data


result = process_data(None)

if result == ErrorCode.SUCCESS:
    print("操作成功")
elif result == ErrorCode.INVALID_INPUT:
    print("无效的输入")
elif result == ErrorCode.FILE_NOT_FOUND:
    print("文件未找到")
# 可以继续添加更多的条件来处理其他错误码
else:
    print("发生未知错误")
