from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union


_LAZY_SDK_SINGLETONS: Dict[str, Callable] = {}


def sdk_command(
    key: str, sdk_cls: Type, *, doc_py_example: str, arg_docstrings: Dict[str, str],
) -> Callable[[Callable], Callable]:
    """Decorator to automatically inject an `_sdk` arg into the wrapped function.

    The arguments to this class are a unique key for the singleton and its type
    (the constructor will be called with no arguments).
    """

    def _inject_typed_sdk_singleton(f: Callable) -> Callable:
        if not doc_py_example:
            raise ValueError(
                f"SDK command '{f.__name__}' must provide a non-empty 'doc_py_example'."
            )

        # TODO: validate docstrings.

        @wraps(f)
        def wrapper(*args, **kwargs):
            if key not in _LAZY_SDK_SINGLETONS:
                _LAZY_SDK_SINGLETONS[key] = sdk_cls()

            return f(*args, _sdk=_LAZY_SDK_SINGLETONS[key], **kwargs)

        # TODO(edoakes): move to parsing docstrings instead.
        wrapper.__doc_py_example__ = doc_py_example  # type: ignore
        wrapper.__arg_docstrings__ = arg_docstrings  # type: ignore

        return wrapper

    return _inject_typed_sdk_singleton
