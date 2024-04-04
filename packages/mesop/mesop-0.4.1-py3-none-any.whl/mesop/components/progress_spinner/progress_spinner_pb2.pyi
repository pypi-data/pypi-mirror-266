"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.message
import sys

if sys.version_info >= (3, 8):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class ProgressSpinnerType(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    COLOR_FIELD_NUMBER: builtins.int
    DIAMETER_FIELD_NUMBER: builtins.int
    STROKE_WIDTH_FIELD_NUMBER: builtins.int
    color: builtins.str
    diameter: builtins.float
    stroke_width: builtins.float
    def __init__(
        self,
        *,
        color: builtins.str | None = ...,
        diameter: builtins.float | None = ...,
        stroke_width: builtins.float | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["color", b"color", "diameter", b"diameter", "stroke_width", b"stroke_width"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["color", b"color", "diameter", b"diameter", "stroke_width", b"stroke_width"]) -> None: ...

global___ProgressSpinnerType = ProgressSpinnerType
