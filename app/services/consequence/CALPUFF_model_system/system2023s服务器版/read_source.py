# -*- coding: utf-8 -*-
"""
根据用户输入，调整对应事故源项，并给出DCF
修改于2023年5月，集成了去除空格，源项核素统一等功能
"""
import pandas as pd
import numpy as np
import os, yaml, glob


def modiy_source(dir_source, dir_out):
    """
    利用pd读取所有源项表，简单判断，删除空表，去处重复核素
    输入源项表，在算例中输出整理后的，名称不变
    """
    source0 = pd.read_excel(io=dir_source, sheet_name=None)
    fn_source0 = dir_source.split('\\')[-1]

    keys = list(source0.keys())

    for key in keys:  # 对于核素数目小于1的直接排除
        if source0[key].shape[0] < 1:
            source0.pop(key)
    keys = list(source0.keys())

    for key in keys:  # 对核素名称有重复的进行处理 2022.12.26
        temp = source0[key]
        temp.drop_duplicates(temp.columns[0], keep='first', inplace=True)
        source0[key] = temp

    # 对表的元素求并集
    source1 = source0[keys[0]]  # 取出第一个表
    column1 = source1.columns[0]

    nt = 0
    for key in keys:
        nt1 = source0[key].shape[1]
        nt = max(nt, nt1)
        source0[key].columns = [column1] + list(range(1, nt1))

    if len(keys) >= 2:
        for i in range(1, len(keys)):
            source1 = pd.merge(source1, source0[keys[i]].iloc[:, 0], how='outer')
    """
    # 核素首字母大写，排序
    """
    source1[column1] = source1[column1].str.strip()  # 2025.5，添加去除空格
    source1[column1] = source1[column1].str.capitalize()
    source1 = source1.sort_values(by=column1, ascending=1)
    source1 = source1.reset_index(drop=True)

    nname = source1[column1].values.tolist()
    nn = source1.shape[0]

    # 依次生成新的核素表,并输出
    with pd.ExcelWriter(os.path.join(dir_out, fn_source0)) as writer:

        for i in range(len(keys)):
            source2 = pd.DataFrame(np.zeros([nn, nt - 1]), index=nname, columns=list(range(1, nt)))
            source2 = source2.rename_axis(column1).reset_index()
            source3 = source0[keys[i]]
            source3 = source3.sort_values(by=column1, ascending=1)
            source3[column1] = source3[column1].str.capitalize()
            nn3, nt3 = source3.shape

            for j in range(nn3):
                index1 = nname.index(source3.iat[j, 0])
                # print(index1)
                source2.iloc[index1, 1:nt3] = source3.iloc[j, 1:nt3]

            source2.to_excel(writer, keys[i], index=False)
    return nname


if __name__ == '__main__':

    # 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with  open('系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)

    with  open('用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)

    '''
    将源项进行处理，之后复制到计算文件位置
    '''
    dir_run = os.path.join(dir_sys['dir_out0'], grd['title'])

    dir_source = os.path.join(dir_sys['dir_model'], 'DCFsource\\*' + grd['source'] + '.xlsx')
    dir_source = glob.glob(dir_source)[0]

    dir_out = os.path.join(dir_run, '7source')

    # 调用函数，对输入源项表格进行处理
    nname = modiy_source(dir_source, dir_out)

    '''
    剂量转换因子处理
    '''
    # 读入原始DCF文件
    fdcf = glob.glob(dir_sys['dir_model'] + '\\DCFsource' + '/*DCF*')

    DCFacute = pd.read_csv(fdcf[0], delim_whitespace=True)
    DCF80 = pd.read_csv(fdcf[1], delim_whitespace=True)
    DCF825 = pd.read_csv(fdcf[2], delim_whitespace=True)

    '''
    初始化DCF文件
    '''
    nn = len(nname)
    nname1 = []
    for name0 in nname:
        nname1.append(name0.replace(' ', ''))
    nname = nname1

    columns = list(DCF80.columns)
    out1 = pd.DataFrame(np.zeros([nn, 7]), columns=columns)
    out1[columns[0]] = nname

    out2 = out1.copy()

    # 对字符串进行比较，寻找DCF825和80中的核素

    for i in range(nn):
        index1 = DCF80[columns[0]].eq(nname[i])
        temp = DCF80.loc[index1, columns[1]:columns[6]]
        if temp.shape[0] == 1:
            out1.iloc[i, 1:7] = temp
    out1 = out1.loc[out1[columns[1]] > 0]

    for i in range(nn):
        index1 = DCF825[columns[0]].eq(nname[i])
        temp = DCF825.loc[index1, columns[1]:columns[6]]
        if temp.shape[0] == 1:
            out2.iloc[i, 1:7] = temp

    # 对两套数据合并，优先采用DCF80中的结果
    out80 = pd.concat([out1, out2])
    out80.drop_duplicates([columns[0]], keep='first', inplace=True)
    out80 = out80.sort_values(by='nuclides')
    out80.index = range(len(out80))

    # 急性剂量转换因子查找，保留原始核素名称
    out3 = pd.DataFrame(np.zeros([nn, 4]), columns=[columns[0], 'red_marr', 'lungs', 'skin'])
    out3[columns[0]] = nname
    for i in range(nn):
        index1 = DCFacute[columns[0]].eq(nname[i].split('(')[0])
        # 对于I-131(ele)类型的进行处理)
        temp = DCFacute.loc[index1, ['red_marr', 'lungs', 'skin']]
        if temp.shape[0] == 1:
            out3.iloc[i, 1:4] = temp

    # 将两个表格拼接
    out80[['red_marr', 'lungs', 'skin']] = out3[['red_marr', 'lungs', 'skin']]
    out80 = out80.sort_values(by='nuclides', ascending=1)

    # 打印输出结果
    out80.to_csv(os.path.join(dir_out, 'selectDCF.csv'), index=False, mode='w')
