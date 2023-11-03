def res_to_json(res):
    # 将查询结果转换为字典列表
    for item in res:
        item_dict = {}
        for column in item.__table__.columns:
            item_dict[column.name] = getattr(item, column.name)
        res.append(item_dict)
    # 将结果列表转换为 JSON 字符串
    return res
