import enum
import modal.secret
import modal_proto.api_pb2
import typing

class BucketType(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):
        ...

    @property
    def proto(self):
        ...

    def __new__(cls, value):
        ...


class _CloudBucketMount:
    bucket_name: str
    secret: typing.Union[modal.secret._Secret, None]
    read_only: bool
    requester_pays: bool
    bucket_type: typing.Union[BucketType, str]

    def __init__(self, bucket_name: str, secret: typing.Union[modal.secret._Secret, None] = None, read_only: bool = False, requester_pays: bool = False, bucket_type: typing.Union[BucketType, str] = 's3') -> None:
        ...

    def __repr__(self):
        ...

    def __eq__(self, other):
        ...


def cloud_bucket_mounts_to_proto(mounts: typing.List[typing.Tuple[str, _CloudBucketMount]]) -> typing.List[modal_proto.api_pb2.CloudBucketMount]:
    ...


class CloudBucketMount:
    bucket_name: str
    secret: typing.Union[modal.secret.Secret, None]
    read_only: bool
    requester_pays: bool
    bucket_type: typing.Union[BucketType, str]

    def __init__(self, bucket_name: str, secret: typing.Union[modal.secret.Secret, None] = None, read_only: bool = False, requester_pays: bool = False, bucket_type: typing.Union[BucketType, str] = 's3') -> None:
        ...

    def __repr__(self):
        ...

    def __eq__(self, other):
        ...
