from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional

noop_decorators: ContextVar[bool] = ContextVar("noop_decorator", default=False)
decorator_src_override: ContextVar[Optional[str]] = ContextVar(
    "decorator_src_override", default=None
)


@contextmanager
def noop_decorators_context(val: bool):
    token = noop_decorators.set(val)
    try:
        yield token
    finally:
        noop_decorators.reset(token)


@contextmanager
def decorator_src_override_context(val: str):
    token = decorator_src_override.set(val)
    try:
        yield token
    finally:
        decorator_src_override.reset(token)
