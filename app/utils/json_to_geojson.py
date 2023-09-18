import geojson


def custom_table_to_geojson(json_data):
    # 创建一个 GeoJSON 特征集合
    features = []

    for item in json_data:
        properties = {}  # 创建一个空字典用于存储属性键值对
        for key, value in item.items():
            properties[key] = value  # 将数据中的键值对添加到属性字典中

        # 创建一个 GeoJSON 特征
        feature = geojson.Feature(
            geometry=geojson.Point((item["longitude"], item["latitude"])),
            properties=properties  # 使用动态属性字典
        )
        features.append(feature)

    # 创建一个 GeoJSON 特征集合
    feature_collection = geojson.FeatureCollection(features)

    # 将 GeoJSON 对象序列化为 JSON 字符串
    geojson_data = geojson.dumps(feature_collection, ensure_ascii=False)

    print(geojson_data)
