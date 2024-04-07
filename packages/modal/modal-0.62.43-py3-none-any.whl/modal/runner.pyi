import modal._output
import modal.app
import modal.client
import modal.object
import multiprocessing.synchronize
import synchronicity.combined_types
import typing
import typing_extensions

_Stub = typing.TypeVar("_Stub")

async def _heartbeat(client, app_id):
    ...


async def _init_local_app_existing(client: modal.client._Client, existing_app_id: str) -> modal.app._LocalApp:
    ...


async def _init_local_app_new(client: modal.client._Client, description: str, app_state: int, environment_name: str = '', interactive=False) -> modal.app._LocalApp:
    ...


async def _init_local_app_from_name(client: modal.client._Client, name: str, namespace, environment_name: str = ''):
    ...


async def _create_all_objects(client: modal.client._Client, app: modal.app._LocalApp, indexed_objects: typing.Dict[str, modal.object._Object], new_app_state: int, environment_name: str, output_mgr: typing.Union[modal._output.OutputManager, None] = None):
    ...


async def _disconnect(client: modal.client._Client, app_id: str, reason: typing.Union[int, None] = None, exc_str: typing.Union[str, None] = None):
    ...


def _run_stub(stub: _Stub, client: typing.Union[modal.client._Client, None] = None, stdout=None, show_progress: bool = True, detach: bool = False, output_mgr: typing.Union[modal._output.OutputManager, None] = None, environment_name: typing.Union[str, None] = None, shell=False, interactive=False) -> typing.AsyncContextManager[_Stub]:
    ...


async def _serve_update(stub, existing_app_id: str, is_ready: multiprocessing.synchronize.Event, environment_name: str) -> None:
    ...


class DeployResult:
    app_id: str

    def __init__(self, app_id: str) -> None:
        ...

    def __repr__(self):
        ...

    def __eq__(self, other):
        ...

    def __setattr__(self, name, value):
        ...

    def __delattr__(self, name):
        ...

    def __hash__(self):
        ...


async def _deploy_stub(stub: _Stub, name: str = None, namespace=1, client=None, stdout=None, show_progress=True, environment_name: typing.Union[str, None] = None, public: bool = False) -> DeployResult:
    ...


async def _interactive_shell(_stub: _Stub, cmd: typing.List[str], environment_name: str = '', **kwargs):
    ...


class __run_stub_spec(typing_extensions.Protocol):
    def __call__(self, stub: _Stub, client: typing.Union[modal.client.Client, None] = None, stdout=None, show_progress: bool = True, detach: bool = False, output_mgr: typing.Union[modal._output.OutputManager, None] = None, environment_name: typing.Union[str, None] = None, shell=False, interactive=False) -> synchronicity.combined_types.AsyncAndBlockingContextManager[_Stub]:
        ...

    def aio(self, stub: _Stub, client: typing.Union[modal.client.Client, None] = None, stdout=None, show_progress: bool = True, detach: bool = False, output_mgr: typing.Union[modal._output.OutputManager, None] = None, environment_name: typing.Union[str, None] = None, shell=False, interactive=False) -> typing.AsyncContextManager[_Stub]:
        ...

run_stub: __run_stub_spec


class __serve_update_spec(typing_extensions.Protocol):
    def __call__(self, stub, existing_app_id: str, is_ready: multiprocessing.synchronize.Event, environment_name: str) -> None:
        ...

    async def aio(self, *args, **kwargs) -> None:
        ...

serve_update: __serve_update_spec


class __deploy_stub_spec(typing_extensions.Protocol):
    def __call__(self, stub: _Stub, name: str = None, namespace=1, client=None, stdout=None, show_progress=True, environment_name: typing.Union[str, None] = None, public: bool = False) -> DeployResult:
        ...

    async def aio(self, *args, **kwargs) -> DeployResult:
        ...

deploy_stub: __deploy_stub_spec


class __interactive_shell_spec(typing_extensions.Protocol):
    def __call__(self, _stub: _Stub, cmd: typing.List[str], environment_name: str = '', **kwargs):
        ...

    async def aio(self, *args, **kwargs):
        ...

interactive_shell: __interactive_shell_spec
