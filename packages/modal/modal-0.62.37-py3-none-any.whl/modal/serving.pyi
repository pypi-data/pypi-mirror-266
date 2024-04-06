import _io
import modal._output
import multiprocessing.context
import multiprocessing.synchronize
import synchronicity.combined_types
import typing
import typing_extensions

_Stub = typing.TypeVar("_Stub")

def _run_serve(stub_ref: str, existing_app_id: str, is_ready: multiprocessing.synchronize.Event, environment_name: str):
    ...


async def _restart_serve(stub_ref: str, existing_app_id: str, environment_name: str, timeout: float = 5.0) -> multiprocessing.context.SpawnProcess:
    ...


async def _terminate(proc: typing.Union[multiprocessing.context.SpawnProcess, None], output_mgr: modal._output.OutputManager, timeout: float = 5.0):
    ...


async def _run_watch_loop(stub_ref: str, app_id: str, output_mgr: modal._output.OutputManager, watcher: typing.AsyncGenerator[typing.Set[str], None], environment_name: str):
    ...


def _get_clean_stub_description(stub_ref: str) -> str:
    ...


def _serve_stub(stub: _Stub, stub_ref: str, stdout: typing.Union[_io.TextIOWrapper, None] = None, show_progress: bool = True, _watcher: typing.Union[typing.AsyncGenerator[typing.Set[str], None], None] = None, environment_name: typing.Union[str, None] = None) -> typing.AsyncContextManager[_Stub]:
    ...


class __serve_stub_spec(typing_extensions.Protocol):
    def __call__(self, stub: _Stub, stub_ref: str, stdout: typing.Union[_io.TextIOWrapper, None] = None, show_progress: bool = True, _watcher: typing.Union[typing.Generator[typing.Set[str], None, None], None] = None, environment_name: typing.Union[str, None] = None) -> synchronicity.combined_types.AsyncAndBlockingContextManager[_Stub]:
        ...

    def aio(self, stub: _Stub, stub_ref: str, stdout: typing.Union[_io.TextIOWrapper, None] = None, show_progress: bool = True, _watcher: typing.Union[typing.AsyncGenerator[typing.Set[str], None], None] = None, environment_name: typing.Union[str, None] = None) -> typing.AsyncContextManager[_Stub]:
        ...

serve_stub: __serve_stub_spec
