# Handling imports and missing dependencies
try:
    import redis
except ImportError:
    redis = None

from launchflow.resource import Resource
from pydantic import BaseModel


def _check_installs():
    if redis is None:
        raise ImportError(
            "redis library is not installed. Please install it with `pip install redis`."
        )


class MemorystoreRedisConnectionInfo(BaseModel):
    host: str
    port: int
    password: str


class MemorystoreRedis(Resource[MemorystoreRedisConnectionInfo]):
    """A Redis resource running on Google Cloud's Memorystore service.

    **Attributes**:
    - `name` (str): The name of the Redis VM resource. This must be globally unique.
    - `memory_size_gb` (int): The memory size of the Redis instance in GB. Defaults to 1.

    Example usage:
    ```python
    import launchflow as lf

    redis = lf.gcp.MemorystoreRedis("my-redis-instance")

    # Set a key-value pair
    client = redis.redis()
    client.set("my-key", "my-value")

    # Async compatible
    async_client = await redis.redis_async()
    await async_client.set("my-key", "my-value")
    ```
    """

    def __init__(self, name: str, *, memory_size_gb: int = 1) -> None:
        super().__init__(
            name=name,
            product_name="gcp_memorystore_redis",
            create_args={"memory_size_gb": memory_size_gb},
        )

    def django_settings(self):
        connection_info = self.connect()
        return {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": f"redis://default:{connection_info.password}@{connection_info.host}:{connection_info.port}",
        }

    def redis(self):
        """Get a Generic Redis Client object from the redis-py library.

        **Returns**:
        - The [Generic Redis Client](https://redis-py.readthedocs.io/en/stable/connections.html#generic-client) from the redis-py library.
        """
        _check_installs()
        connection_info = self.connect()
        return redis.Redis(
            host=connection_info.host,
            port=connection_info.port,
            password=connection_info.password,
            decode_responses=True,
        )

    async def redis_async(self):
        """Get an Async Redis Client object from the redis-py library.

        **Returns**:
        - The [Async Redis Client object](https://redis-py.readthedocs.io/en/stable/connections.html#async-client) from the redis-py library.
        """
        _check_installs()
        connection_info = await self.connect_async()
        return await redis.asyncio.from_url(
            f"redis://{connection_info.host}:{connection_info.port}",
            password=connection_info.password,
            decode_responses=True,
        )
