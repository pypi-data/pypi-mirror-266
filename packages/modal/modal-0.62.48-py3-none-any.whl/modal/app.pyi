import google.protobuf.message
import modal.client
import modal_proto.api_pb2
import typing
import typing_extensions

_Function = typing.TypeVar("_Function")

class _LocalApp:
    tag_to_object_id: typing.Dict[str, str]
    app_id: str
    app_page_url: str
    environment_name: str
    interactive: bool

    def __init__(self, app_id: str, app_page_url: str, tag_to_object_id: typing.Union[typing.Dict[str, str], None] = None, environment_name: typing.Union[str, None] = None, interactive: bool = False):
        ...


class _ContainerApp:
    app_id: typing.Union[str, None]
    environment_name: typing.Union[str, None]
    tag_to_object_id: typing.Dict[str, str]
    object_handle_metadata: typing.Dict[str, typing.Union[google.protobuf.message.Message, None]]
    is_interactivity_enabled: bool
    function_def: typing.Union[modal_proto.api_pb2.Function, None]
    fetching_inputs: bool

    def __init__(self):
        ...


def _reset_container_app():
    ...


_container_app: _ContainerApp

async def _init_container_app(client: modal.client._Client, app_id: str, environment_name: str = '', function_def: typing.Union[modal_proto.api_pb2.Function, None] = None):
    ...


class __init_container_app_spec(typing_extensions.Protocol):
    def __call__(self, client: modal.client.Client, app_id: str, environment_name: str = '', function_def: typing.Union[modal_proto.api_pb2.Function, None] = None):
        ...

    async def aio(self, *args, **kwargs):
        ...

init_container_app: __init_container_app_spec


async def _interact(client: typing.Union[modal.client._Client, None] = None) -> None:
    ...


class __interact_spec(typing_extensions.Protocol):
    def __call__(self, client: typing.Union[modal.client.Client, None] = None) -> None:
        ...

    async def aio(self, *args, **kwargs) -> None:
        ...

interact: __interact_spec


def is_local() -> bool:
    ...


async def _list_apps(env: str, client: typing.Union[modal.client._Client, None] = None) -> typing.List[modal_proto.api_pb2.AppStats]:
    ...


class __list_apps_spec(typing_extensions.Protocol):
    def __call__(self, env: str, client: typing.Union[modal.client.Client, None] = None) -> typing.List[modal_proto.api_pb2.AppStats]:
        ...

    async def aio(self, *args, **kwargs) -> typing.List[modal_proto.api_pb2.AppStats]:
        ...

list_apps: __list_apps_spec
