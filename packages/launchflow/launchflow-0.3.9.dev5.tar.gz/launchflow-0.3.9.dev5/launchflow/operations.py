from dataclasses import dataclass
from typing import Callable, Coroutine, Dict, Literal, Optional

from launchflow.clients.client import LaunchFlowAsyncClient
from launchflow.clients.response_schemas import OperationResponse, OperationStatus

from launchflow import exceptions


@dataclass
class AsyncOp:
    operation_id: Optional[str]
    client: LaunchFlowAsyncClient
    _op: Callable[[], Coroutine[None, None, OperationResponse]]

    async def run(self):
        if self.operation_id is not None:
            raise exceptions.OperationAlreadyStarted(str(self))

        operation = await self._op()
        self.operation_id = operation.id

    async def stream_status(self):
        if self.operation_id is None:
            raise exceptions.OperationNotStarted(str(self))
        async for status in self.client.operations.stream_operation_status(
            self.operation_id
        ):
            yield status

    async def get_status(self) -> OperationStatus:
        if self.operation_id is None:
            raise exceptions.OperationNotStarted(str(self))
        return await self.client.operations.get_operation_status(self.operation_id)

    async def done(self):
        return (await self.get_status()).is_final()

    async def result(self) -> str:
        # starts and blocks until the operation is done
        await self.run()
        async for status in self.stream_status():
            if status.is_final():
                return status


@dataclass
class AsyncResourceOp(AsyncOp):
    resource_ref: str
    _type: Literal["create", "replace"]
    _create_args: Optional[Dict] = None
    _replace_args: Optional[Dict] = None


@dataclass
class AsyncResourceNoOp(AsyncOp):
    resource_ref: str
    _type: Literal["noop"] = "noop"

    async def run(self):
        pass

    async def stream_status(self):
        yield OperationStatus.SUCCESS

    async def get_status(self):
        return OperationStatus.SUCCESS

    async def done(self):
        return True

    async def result(self):
        return OperationStatus.SUCCESS
