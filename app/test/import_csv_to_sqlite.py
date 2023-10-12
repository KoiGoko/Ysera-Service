import csv
import sqlite3
import pandas as pd


# 1. 从CSV文件中读取台站信息
def save_to_db(csv_file, db_file):
    df = pd.read_csv(csv_file, encoding='utf-8')
    df = df.dropna(axis=1, how='all')
    df = df.dropna(axis=0, how='all')

    conn = sqlite3.connect(db_file)
    df.to_sql('nuclear_stations', conn, if_exists='replace', index=False)
    # 关闭数据库连接
    conn.close()


if __name__ == "__main__":
    # 输入CSV文件和SQLite数据库文件的路径
    csv_file_path = '核电厂地理位置 - 英文版.CSV'
    sqlite_db_file_path = 'nuclear_stations.sqlite'

    # 读取CSV文件
    save_to_db(csv_file_path, sqlite_db_file_path)

    # 读取SQLite数据库文件
    conn = sqlite3.connect(sqlite_db_file_path)
    df = pd.read_sql('select * from stations', conn)
    print(df)
    print('Done')
