from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def _maybe_inplace(obj: T, inplace: bool) -> T:
    if inplace:
        return obj
    else:
        return obj.copy(deep=True)
