import numpy as np
import dask
from dask.distributed import Client


# 原生的 NumPy 程序
def numpy_computation(x):
    return np.sum(x ** 2)


# 单机版 Dask
def dask_local_computation(x):
    result = dask.delayed(numpy_computation)(x)
    return dask.compute(result)[0]


# 分布式版 Dask
def dask_distributed_computation(x):
    with Client() as client:
        future_result = client.submit(numpy_computation, x)
        result = future_result.result()
    return result


# 示例数据
data = np.random.random((1000, 1000))

# 切换为单机版 Dask
result_local = dask_local_computation(data)
print("Result (Local Dask):", result_local)

# 切换为分布式版 Dask
result_distributed = dask_distributed_computation(data)
print("Result (Distributed Dask):", result_distributed)
