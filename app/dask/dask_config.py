import dask
from dask.distributed import Client, LocalCluster

# 配置 Dask 的默认行为，以便在需要时启动分布式集群
dask.config.set(scheduler="threads")  # 默认使用多线程


def create_local_cluster():
    # 创建一个本地集群（单机模式）
    cluster = LocalCluster()
    return cluster


def create_distributed_cluster():
    # 创建一个分布式集群
    cluster = LocalCluster()  # 在实际应用中，可以使用不同的配置来连接远程工作节点
    return cluster


def use_native_numpy():
    # 使用原生 NumPy（不使用 Dask）
    dask.config.set(scheduler="single-threaded")  # 单线程模式


def switch_to_dask():
    # 切换回使用 Dask 集群
    dask.config.set(scheduler="threads")  # 多线程模式


# 创建一个 Dask 客户端
client = Client()

# 在单机模式下使用 Dask
result = client.submit(lambda x: x ** 2, 10).result()
print(f"单机 Dask 计算结果: {result}")

# 切换到分布式 Dask 集群
distributed_cluster = create_distributed_cluster()
client.close()  # 关闭当前客户端
client = Client(cluster=distributed_cluster)

# 在分布式模式下使用 Dask
result = client.submit(lambda x: x ** 2, 10).result()
print(f"分布式 Dask 计算结果: {result}")

# 切换回原生 NumPy 模式
use_native_numpy()

# 使用原生 NumPy
import numpy as np

array = np.array([1, 2, 3, 4, 5])
squared = np.square(array)
print(f"原生 NumPy 计算结果: {squared}")

# 切换回使用 Dask 集群
switch_to_dask()

# 继续在 Dask 集群中工作
result = client.submit(lambda x: x ** 2, 10).result()
print(f"单机 Dask 计算结果: {result}")

# 关闭客户端和集群
client.close()
distributed_cluster.close()
