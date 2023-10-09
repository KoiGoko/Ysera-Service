import numpy as np

__author__ = 'Nan Jia'
__email__ = 'KoiGoko@outlook.com'


# 撤离分布算法模块


# 撤离泊松分布
def poisson_distribution(count, lambd=5):
    poisson_array = np.random.poisson(lam=lambd, size=count)
    return poisson_array


# # 撤离二项分布
def binomial_distribution(count, n=10, p=0.5):
    # 生成撤离二项分布的数组
    binomial_array = np.random.negative_binomial(n=n, p=p, size=count)
    return binomial_array


# 撤离均匀分布
def uniform_distribution(count):
    uniforms = np.arange(0, count, 1)
    return uniforms


def truncated_normal_distribution(count, mean=0, std=1, lower=-1, upper=1):
    # 生成截断正态分布的数组
    normal_array = np.random.normal(loc=mean, scale=std, size=count)
    truncated_array = np.clip(normal_array, lower, upper)
    return truncated_array


def truncated_log_normal_distribution(count, mean=0, std=1, lower=0, upper=10):
    # 生成对数正态分布的数组
    log_normal_array = np.random.lognormal(mean=mean, sigma=std, size=count)

    # 对数组进行截断或裁剪
    truncated_array = np.clip(log_normal_array, lower, upper)
    return truncated_array


def truncated_exponential_distribution(count, lambd=1, lower=0, upper=10):
    # 生成指数分布的数组
    exponential_array = np.random.exponential(scale=1 / lambd, size=count)

    # 对数组进行截断或裁剪
    truncated_array = np.clip(exponential_array, lower, upper)
    return truncated_array


def distribution_main():
    pass


if __name__ == '__main__':
    print('撤离分布算法模块')
