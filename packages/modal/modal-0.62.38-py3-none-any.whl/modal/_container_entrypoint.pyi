import asyncio.queues
import collections.abc
import modal.client
import modal.functions
import modal.stub
import modal_proto.api_pb2
import typing
import typing_extensions

class UserException(Exception):
    ...

class UserCodeEventLoop:
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, traceback):
        ...

    def run(self, coro):
        ...


class _FunctionIOManager:
    def __init__(self, container_args: modal_proto.api_pb2.ContainerArguments, client: modal.client._Client):
        ...

    async def _run_heartbeat_loop(self):
        ...

    async def _heartbeat_handle_cancellations(self) -> bool:
        ...

    def heartbeats(self):
        ...

    def stop_heartbeat(self):
        ...

    async def get_serialized_function(self) -> typing.Tuple[typing.Union[typing.Any, None], typing.Callable]:
        ...

    def serialize(self, obj: typing.Any) -> bytes:
        ...

    def deserialize(self, data: bytes) -> typing.Any:
        ...

    def serialize_data_format(self, obj: typing.Any, data_format: int) -> bytes:
        ...

    def deserialize_data_format(self, data: bytes, data_format: int) -> typing.Any:
        ...

    def get_data_in(self, function_call_id: str) -> typing.AsyncIterator[typing.Any]:
        ...

    async def put_data_out(self, function_call_id: str, start_index: int, data_format: int, messages_bytes: typing.List[typing.Any]) -> None:
        ...

    async def generator_output_task(self, function_call_id: str, data_format: int, message_rx: asyncio.queues.Queue) -> None:
        ...

    async def _queue_create(self, size: int) -> asyncio.queues.Queue:
        ...

    async def _queue_put(self, queue: asyncio.queues.Queue, value: typing.Any) -> None:
        ...

    async def populate_input_blobs(self, item: modal_proto.api_pb2.FunctionInput):
        ...

    def get_average_call_time(self) -> float:
        ...

    def get_max_inputs_to_fetch(self):
        ...

    def _generate_inputs(self) -> typing.AsyncIterator[typing.Tuple[str, str, modal_proto.api_pb2.FunctionInput]]:
        ...

    def run_inputs_outputs(self, input_concurrency: int = 1) -> typing.AsyncIterator[typing.Tuple[str, str, typing.Any, typing.Any]]:
        ...

    async def _push_output(self, input_id, started_at: float, data_format=0, **kwargs):
        ...

    def serialize_exception(self, exc: BaseException) -> typing.Union[bytes, None]:
        ...

    def serialize_traceback(self, exc: BaseException) -> typing.Tuple[typing.Union[bytes, None], typing.Union[bytes, None]]:
        ...

    def handle_user_exception(self) -> typing.AsyncGenerator[None, None]:
        ...

    def handle_input_exception(self, input_id, started_at: float) -> typing.AsyncGenerator[None, None]:
        ...

    async def complete_call(self, started_at):
        ...

    async def push_output(self, input_id, started_at: float, data: typing.Any, data_format: int) -> None:
        ...

    async def restore(self) -> None:
        ...

    async def checkpoint(self) -> None:
        ...

    async def volume_commit(self, volume_ids: typing.List[str]) -> None:
        ...


class FunctionIOManager:
    def __init__(self, container_args: modal_proto.api_pb2.ContainerArguments, client: modal.client.Client):
        ...

    class ___run_heartbeat_loop_spec(typing_extensions.Protocol):
        def __call__(self):
            ...

        async def aio(self, *args, **kwargs):
            ...

    _run_heartbeat_loop: ___run_heartbeat_loop_spec

    class ___heartbeat_handle_cancellations_spec(typing_extensions.Protocol):
        def __call__(self) -> bool:
            ...

        async def aio(self, *args, **kwargs) -> bool:
            ...

    _heartbeat_handle_cancellations: ___heartbeat_handle_cancellations_spec

    def heartbeats(self):
        ...

    def stop_heartbeat(self):
        ...

    class __get_serialized_function_spec(typing_extensions.Protocol):
        def __call__(self) -> typing.Tuple[typing.Union[typing.Any, None], typing.Callable]:
            ...

        async def aio(self, *args, **kwargs) -> typing.Tuple[typing.Union[typing.Any, None], typing.Callable]:
            ...

    get_serialized_function: __get_serialized_function_spec

    def serialize(self, obj: typing.Any) -> bytes:
        ...

    def deserialize(self, data: bytes) -> typing.Any:
        ...

    def serialize_data_format(self, obj: typing.Any, data_format: int) -> bytes:
        ...

    def deserialize_data_format(self, data: bytes, data_format: int) -> typing.Any:
        ...

    class __get_data_in_spec(typing_extensions.Protocol):
        def __call__(self, function_call_id: str) -> typing.Iterator[typing.Any]:
            ...

        def aio(self, function_call_id: str) -> typing.AsyncIterator[typing.Any]:
            ...

    get_data_in: __get_data_in_spec

    class __put_data_out_spec(typing_extensions.Protocol):
        def __call__(self, function_call_id: str, start_index: int, data_format: int, messages_bytes: typing.List[typing.Any]) -> None:
            ...

        async def aio(self, *args, **kwargs) -> None:
            ...

    put_data_out: __put_data_out_spec

    class __generator_output_task_spec(typing_extensions.Protocol):
        def __call__(self, function_call_id: str, data_format: int, message_rx: asyncio.queues.Queue) -> None:
            ...

        async def aio(self, *args, **kwargs) -> None:
            ...

    generator_output_task: __generator_output_task_spec

    class ___queue_create_spec(typing_extensions.Protocol):
        def __call__(self, size: int) -> asyncio.queues.Queue:
            ...

        async def aio(self, *args, **kwargs) -> asyncio.queues.Queue:
            ...

    _queue_create: ___queue_create_spec

    class ___queue_put_spec(typing_extensions.Protocol):
        def __call__(self, queue: asyncio.queues.Queue, value: typing.Any) -> None:
            ...

        async def aio(self, *args, **kwargs) -> None:
            ...

    _queue_put: ___queue_put_spec

    class __populate_input_blobs_spec(typing_extensions.Protocol):
        def __call__(self, item: modal_proto.api_pb2.FunctionInput):
            ...

        async def aio(self, *args, **kwargs):
            ...

    populate_input_blobs: __populate_input_blobs_spec

    def get_average_call_time(self) -> float:
        ...

    def get_max_inputs_to_fetch(self):
        ...

    class ___generate_inputs_spec(typing_extensions.Protocol):
        def __call__(self) -> typing.Iterator[typing.Tuple[str, str, modal_proto.api_pb2.FunctionInput]]:
            ...

        def aio(self) -> typing.AsyncIterator[typing.Tuple[str, str, modal_proto.api_pb2.FunctionInput]]:
            ...

    _generate_inputs: ___generate_inputs_spec

    class __run_inputs_outputs_spec(typing_extensions.Protocol):
        def __call__(self, input_concurrency: int = 1) -> typing.Iterator[typing.Tuple[str, str, typing.Any, typing.Any]]:
            ...

        def aio(self, input_concurrency: int = 1) -> typing.AsyncIterator[typing.Tuple[str, str, typing.Any, typing.Any]]:
            ...

    run_inputs_outputs: __run_inputs_outputs_spec

    class ___push_output_spec(typing_extensions.Protocol):
        def __call__(self, input_id, started_at: float, data_format=0, **kwargs):
            ...

        async def aio(self, *args, **kwargs):
            ...

    _push_output: ___push_output_spec

    def serialize_exception(self, exc: BaseException) -> typing.Union[bytes, None]:
        ...

    def serialize_traceback(self, exc: BaseException) -> typing.Tuple[typing.Union[bytes, None], typing.Union[bytes, None]]:
        ...

    class __handle_user_exception_spec(typing_extensions.Protocol):
        def __call__(self) -> typing.Generator[None, None, None]:
            ...

        def aio(self) -> typing.AsyncGenerator[None, None]:
            ...

    handle_user_exception: __handle_user_exception_spec

    class __handle_input_exception_spec(typing_extensions.Protocol):
        def __call__(self, input_id, started_at: float) -> typing.Generator[None, None, None]:
            ...

        def aio(self, input_id, started_at: float) -> typing.AsyncGenerator[None, None]:
            ...

    handle_input_exception: __handle_input_exception_spec

    class __complete_call_spec(typing_extensions.Protocol):
        def __call__(self, started_at):
            ...

        async def aio(self, *args, **kwargs):
            ...

    complete_call: __complete_call_spec

    class __push_output_spec(typing_extensions.Protocol):
        def __call__(self, input_id, started_at: float, data: typing.Any, data_format: int) -> None:
            ...

        async def aio(self, *args, **kwargs) -> None:
            ...

    push_output: __push_output_spec

    class __restore_spec(typing_extensions.Protocol):
        def __call__(self) -> None:
            ...

        async def aio(self, *args, **kwargs) -> None:
            ...

    restore: __restore_spec

    class __checkpoint_spec(typing_extensions.Protocol):
        def __call__(self) -> None:
            ...

        async def aio(self, *args, **kwargs) -> None:
            ...

    checkpoint: __checkpoint_spec

    class __volume_commit_spec(typing_extensions.Protocol):
        def __call__(self, volume_ids: typing.List[str]) -> None:
            ...

        async def aio(self, *args, **kwargs) -> None:
            ...

    volume_commit: __volume_commit_spec


def call_function_sync(function_io_manager, imp_fun: ImportedFunction):
    ...


async def call_function_async(function_io_manager, imp_fun: ImportedFunction):
    ...


class ImportedFunction:
    obj: typing.Any
    fun: typing.Callable
    stub: typing.Union[modal.stub._Stub, None]
    is_async: bool
    is_generator: bool
    data_format: int
    input_concurrency: int
    is_auto_snapshot: bool
    function: modal.functions._Function

    def __init__(self, obj: typing.Any, fun: typing.Callable, stub: typing.Union[modal.stub._Stub, None], is_async: bool, is_generator: bool, data_format: int, input_concurrency: int, is_auto_snapshot: bool, function: modal.functions._Function) -> None:
        ...

    def __repr__(self):
        ...

    def __eq__(self, other):
        ...


def import_function(function_def: modal_proto.api_pb2.Function, ser_cls, ser_fun, ser_params: typing.Union[bytes, None], function_io_manager, client: modal.client.Client) -> ImportedFunction:
    ...


def call_lifecycle_functions(event_loop: UserCodeEventLoop, function_io_manager, funcs: collections.abc.Iterable[typing.Callable]) -> None:
    ...


def main(container_args: modal_proto.api_pb2.ContainerArguments, client: modal.client.Client):
    ...


MAX_OUTPUT_BATCH_SIZE: 'int'

RTT_S: 'float'