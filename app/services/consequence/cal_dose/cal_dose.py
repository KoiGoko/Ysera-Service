def cal_dose(radiation_type, exposure, duration):
    """
    计算辐射剂量

    参数：
    radiation_type: 辐射类型，比如 'alpha'、'beta'、'gamma'
    exposure: 辐射源的暴露强度，单位微戈瑞每小时（μGy/h）
    duration: 暴露时间，单位小时

    返回：
    辐射剂量，单位西弗（Sv）
    """
    # 辐射质量因子
    quality_factors = {'alpha': 20, 'beta': 1, 'gamma': 1}

    # 计算剂量
    dose = exposure * duration * quality_factors.get(radiation_type, 1)

    return dose / 1000  # 转换单位为Sv
