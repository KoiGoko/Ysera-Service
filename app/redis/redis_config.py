import aioredis


async def create_redis_pool():
    # 创建 Redis 连接池
    pool = await aioredis.create_pool("redis://localhost", minsize=5, maxsize=10)
    return pool


async def set_value(redis_pool, key, value):
    # 在 Redis 中存储数据
    async with redis_pool.get() as redis:
        await redis.set(key, value)


async def get_value(redis_pool, key):
    # 从 Redis 中检索数据
    async with redis_pool.get() as redis:
        value = await redis.get(key)
    return value
