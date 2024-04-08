import contextlib

from .client import LaunchFlowAsyncClient


@contextlib.asynccontextmanager
async def async_launchflow_client_ctx():
    launchflow_async_client = LaunchFlowAsyncClient()
    try:
        yield launchflow_async_client
    finally:
        await launchflow_async_client.close()
