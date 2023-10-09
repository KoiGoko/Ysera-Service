from evacuate.src.utils import input_args

_author_ = 'Nan Jia'
_email_ = 'KoiGoko@outlook.com'

evacuate = {}
vehicle = {}


def init_cfg(_cfg_path):
    _evacuate = input_args(_cfg_path, 'evacuate')
    _vehicle = input_args(_cfg_path, 'vehicle')
    evacuate.update(_evacuate)
    vehicle.update(_vehicle)


def pro_remain_population():
    default_population = evacuate['default_population']
    vehicle_number = evacuate['vehicle_number']
    vehicle_capacity = vehicle['vehicle_capacity']
    for key, value in default_population.items():
        for key1, value1 in vehicle_number[key].items():
            default_population[key] -= vehicle_capacity[key1] * value1
            if default_population[key] < 0:
                default_population[key] = 0

    # 一次分配
    one_population = {}
    public_routes = evacuate['public_routes']
    pub_vehicle_types = {}
    for key, value in public_routes.items():
        for key1, value1 in value.items():
            total = 0
            pub_vehicle_type = {}
            for key2, value2 in value1.items():
                total += vehicle_capacity[key2] * value2
                pub_vehicle_type[key2] = value2
            if key1 not in pub_vehicle_types.keys():
                pub_vehicle_types[key1] = pub_vehicle_type
            else:
                for key3, value3 in pub_vehicle_type.items():
                    if key3 not in pub_vehicle_types[key1].keys():
                        pub_vehicle_types[key1][key3] = value3
                    else:
                        pub_vehicle_types[key1][key3] += value3

            if key1 not in one_population.keys():
                one_population[key1] = total
            else:
                one_population[key1] += total

    # 贪心策略开始，默认策略是会让车辆尽可能多的搭载人数，然后尽可能少进行来回的往返
    vehicle_capacity_order = sorted(vehicle_capacity.keys(), key=lambda x: vehicle_capacity[x], reverse=True)

    tags = {}

    for k, v in default_population.items():
        if v != 0 and one_population[k] > v:
            print(f'请注意，公共车辆派遣大于了撤离点‘{k}’的人口数量, ')
            tags[k] = {'all': 1}

    for k, v in default_population.items():
        if v == 0:
            tags[k] = {'all': 0}
            continue

        tag = {}

        if k in one_population.keys():
            pub_types = sorted(pub_vehicle_types[k].keys(), key=lambda x: vehicle_capacity_order.index(x))
            ladder = [one_population[k]]
            flag = ['all']
            for pub_type in pub_types:
                ladder.append(vehicle_capacity[pub_type] * pub_vehicle_types[k][pub_type])
                flag.append(pub_type + '_all')

            st = 0

            while v > 0 and st < len(ladder):
                if st == 0:
                    if v >= ladder[st]:
                        count = v // ladder[st]
                        v = v % ladder[st]
                        tag[flag[st]] = count

                    st += 1
                    continue
                if v >= ladder[st]:
                    v = v - ladder[st]
                    st += 1
                    if flag[st] not in tag.keys():
                        tag[flag[st]] = 1
                    tag[flag[st]] += 1
                else:
                    cap = vehicle_capacity[flag[st].split('_')[0]]
                    factor = (v + cap - 1) // cap
                    tag[flag[st].split('_')[0]] = factor
                    break
            if k not in tags.keys():
                tags[k] = tag
    # 贪心策略结束
    # 返回分配策略
    print(tags)
    return tags


def dynamic_public(cfg_path):
    init_cfg(cfg_path)
    tags = pro_remain_population()
    return tags


if __name__ == '__main__':
    dynamic_public(r'F:\厂址应急道路专题数据\5km晴昼')
    print('公共车辆行程分配策略模块')
