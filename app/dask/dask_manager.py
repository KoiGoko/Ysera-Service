import dask
from dask.distributed import Client, LocalCluster


class DaskManager:
    def __init__(self):
        self.client = None

    def create_local_cluster(self):
        cluster = LocalCluster()
        return cluster

    def create_distributed_cluster(self):
        cluster = LocalCluster()  # 在实际应用中，可以使用不同的配置来连接远程工作节点
        return cluster

    def use_native_numpy(self):
        dask.config.set(scheduler="single-threaded")  # 单线程模式

    def switch_to_dask(self):
        dask.config.set(scheduler="threads")  # 多线程模式

    def start_client(self, cluster=None):
        self.client = Client(cluster=cluster)

    def close_client(self):
        if self.client:
            self.client.close()

    def close_cluster(self, cluster):
        if cluster:
            cluster.close()


# 使用示例
dask_manager = DaskManager()

# 在算法开始前设置 DaskManager
dask_manager.use_native_numpy()

# 使用原生 NumPy
import numpy as np

array = np.array([1, 2, 3, 4, 5])
squared = np.square(array)
print(f"原生 NumPy 计算结果: {squared}")

# 切换回使用 Dask 集群
dask_manager.switch_to_dask()

# 在算法中需要使用 Dask 时，启动 Dask 客户端
local_cluster = dask_manager.create_local_cluster()
dask_manager.start_client(cluster=local_cluster)

# 在 Dask 模式下工作
result = dask_manager.client.submit(lambda x: x ** 2, 10).result()
print(f"Dask 计算结果: {result}")

# 关闭 Dask 客户端和集群
dask_manager.close_client()
dask_manager.close_cluster(local_cluster)
