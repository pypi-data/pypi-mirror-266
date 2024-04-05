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


class ComputeEngineRedisConnectionInfo(BaseModel):
    host: str
    port: int
    password: str


class ComputeEngineRedis(Resource[ComputeEngineRedisConnectionInfo]):
    """A Redis resource running on a VM in Google Compute Engine.

    **Attributes**:
    - `name` (str): The name of the Redis VM resource. This must be globally unique.

    Example usage:
    ```python
    import launchflow as lf

    redis = lf.gcp.ComputeEngineRedis("my-redis-instance")

    # Set a key-value pair
    client = redis.redis()
    client.set("my-key", "my-value")

    # Async compatible
    async_client = await redis.redis_async()
    await async_client.set("my-key", "my-value")
    ```
    """

    def __init__(self, name: str) -> None:
        super().__init__(
            name=name,
            product_name="gcp_compute_engine_redis",
            create_args={},
        )

        self._async_pool = None
        self._sync_client = None

    def django_settings(self):
        connection_info = self.connect()
        return {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": f"redis://default:{connection_info.password}@{connection_info.host}:{connection_info.port}",
        }

    def redis(self, *, decode_responses: bool = True):
        """Get a Generic Redis Client object from the redis-py library.

        **Returns**:
        - The [Generic Redis Client](https://redis-py.readthedocs.io/en/stable/connections.html#generic-client) from the redis-py library.
        """
        _check_installs()
        connection_info = self.connect()
        if self._sync_client is None:
            self._sync_client = redis.Redis(
                host=connection_info.host,
                port=connection_info.port,
                password=connection_info.password,
                decode_responses=decode_responses,
            )
        return self._sync_client

    async def redis_async(self, *, decode_responses: bool = True):
        """Get an Async Redis Client object from the redis-py library.

        **Returns**:
        - The [Async Redis Client object](https://redis-py.readthedocs.io/en/stable/connections.html#async-client) from the redis-py library.
        """
        _check_installs()
        connection_info = await self.connect_async()
        if self._async_pool is None:
            self._async_pool = await redis.asyncio.from_url(
                f"redis://{connection_info.host}:{connection_info.port}",
                password=connection_info.password,
                decode_responses=decode_responses,
            )
        return self._async_pool
