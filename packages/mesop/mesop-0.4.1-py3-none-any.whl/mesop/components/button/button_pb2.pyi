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
class ButtonType(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    COLOR_FIELD_NUMBER: builtins.int
    DISABLE_RIPPLE_FIELD_NUMBER: builtins.int
    DISABLED_FIELD_NUMBER: builtins.int
    ON_CLICK_HANDLER_ID_FIELD_NUMBER: builtins.int
    TYPE_INDEX_FIELD_NUMBER: builtins.int
    TYPE_FIELD_NUMBER: builtins.int
    color: builtins.str
    disable_ripple: builtins.bool
    disabled: builtins.bool
    on_click_handler_id: builtins.str
    type_index: builtins.int
    """Type has two properties:
    |type_index| is used for rendering
    |type| is used for editor value
    """
    type: builtins.str
    def __init__(
        self,
        *,
        color: builtins.str | None = ...,
        disable_ripple: builtins.bool | None = ...,
        disabled: builtins.bool | None = ...,
        on_click_handler_id: builtins.str | None = ...,
        type_index: builtins.int | None = ...,
        type: builtins.str | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["color", b"color", "disable_ripple", b"disable_ripple", "disabled", b"disabled", "on_click_handler_id", b"on_click_handler_id", "type", b"type", "type_index", b"type_index"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["color", b"color", "disable_ripple", b"disable_ripple", "disabled", b"disabled", "on_click_handler_id", b"on_click_handler_id", "type", b"type", "type_index", b"type_index"]) -> None: ...

global___ButtonType = ButtonType
