import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import seaborn as sns
import os
import glob


def process_evacuate_graph(path, graph_title, output_select):
    evacuate_path = os.path.join(path, 'evacuate.xlsx')
    evacuate_datas = pd.read_excel(evacuate_path, sheet_name=None, index_col=0)
    evacuate_names = list(evacuate_datas.keys())

    max_start_time = max([df.iloc[3, -1] for df in evacuate_datas.values()])

    sns.set()

    zh_name = {
        'dianchang_huaneng': '电厂-华能',
        'dianchang_zhonghe': '电厂-中核',
        'changmen': '长门村',
        'tiantang': '天堂村',
        'yujiadi': '渔家地村',
        'wuqu': '武曲村',
        'doumi': '斗米村',
        'jishi': '积石村',
        'yuyangli': '渔洋里村',
        'yuyanghan': '渔洋垾村',
        'qiuzhugang': '秋竹岗村',
        'zhizhuwang': '蜘蛛网村',
        'tingxiaxi': '亭下溪村',
        'xiayangcheng': '下洋城村',
        'gaoluo': '高罗海滩旅游景点',
        'dajing': '大京村',
        'zucuo': '祖厝村',
        'chuanlu': '传胪村',
        'changchun': '长春镇'
    }

    plt.figure(figsize=(10, 6))
    for name in evacuate_names:
        pops = evacuate_datas[name].loc['sum'].values
        times = evacuate_datas[name].loc['start_times'].values / 3600
        pops = np.append(pops, pops[-1])
        times = np.append(times, max_start_time / 3600) / 1.8

        sns.lineplot(x=times, y=pops, label=zh_name[name])

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    plt.title(graph_title)
    plt.xlabel('时间（小时）')
    plt.ylabel('撤离人数')
    plt.legend(title='待撤离点')

    ax = plt.gca()
    ax.legend(loc='upper left')

    if output_select == 1:
        graph_path = os.path.join(os.path.dirname(path), '图表')
        os.makedirs(graph_path, exist_ok=True)
        plt.savefig(os.path.join(graph_path, 'evacuate_' + graph_title + '.png'))
    else:
        plt.savefig(os.path.join(path, 'evacuate_' + graph_title + '.png'))


def process_settlement_graph(path, graph_title, output_select):
    settlement_path = os.path.join(path, 'settlement.xlsx')
    evacuate_path = os.path.join(path, 'evacuate.xlsx')
    evacuate_names = list(pd.read_excel(evacuate_path, sheet_name=None, index_col=0).keys())

    settlement_datas = pd.read_excel(
        settlement_path,
        sheet_name=[sheet for sheet in pd.ExcelFile(settlement_path).sheet_names
                    if sheet not in evacuate_names], index_col=0)

    settlement_names = list(settlement_datas.keys())

    max_start_time = max([df.iloc[3, -1] for df in settlement_datas.values()])

    sns.set()

    plt.figure(figsize=(10, 6))
    for name in settlement_names:
        pops = settlement_datas[name].loc['starts'].values
        times = settlement_datas[name].loc['start_times'].values / 3600
        pops = np.append(pops, pops[-1])
        times = np.append(times, max_start_time / 3600) / 1.8

        sns.lineplot(x=times, y=pops, label=name)

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    plt.title(graph_title)
    plt.xlabel('时间（小时）')
    plt.ylabel('到达安置点人数')
    plt.legend(title='安置点')

    ax = plt.gca()
    ax.legend(loc='upper left')

    if output_select == 1:
        graph_path = os.path.join(os.path.dirname(path), '图表')
        os.makedirs(graph_path, exist_ok=True)
        plt.savefig(os.path.join(graph_path, 'settlement_' + graph_title + '.png'))
    else:
        plt.savefig(os.path.join(path, 'settlement_' + graph_title + '.png'))


def process_road_graph(road_id):
    pass


if __name__ == '__main__':
    paths = glob.glob(r'E:\厂址应急道路专题数据\*')

    output_select = 1

    for path in paths:
        graph_title = os.path.basename(path)

        if path.endswith('图表'):
            continue

        process_evacuate_graph(path, graph_title, output_select)
        process_settlement_graph(path, graph_title, output_select)
