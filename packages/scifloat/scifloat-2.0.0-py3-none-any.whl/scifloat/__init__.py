from typing import SupportsFloat, SupportsIndex, SupportsInt

from typing_extensions import Buffer, TypeAlias

ReadableBuffer: TypeAlias = Buffer
ConvertibleToInt: TypeAlias = str | ReadableBuffer | SupportsInt | SupportsIndex
ConvertibleToFloat: TypeAlias = str | ReadableBuffer | SupportsFloat | SupportsIndex
ConvertibleToList: TypeAlias = (
    str | tuple | list | ReadableBuffer | SupportsFloat | SupportsIndex
)

__all__ = [n for n in globals()]
