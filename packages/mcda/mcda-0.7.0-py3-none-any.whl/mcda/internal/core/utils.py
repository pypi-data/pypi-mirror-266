from typing import Callable, TypeVar

T = TypeVar("T")


def set_module(module: str) -> Callable[[T], T]:
    """Decorate class to change its module prefix in the name.

    This is intended for the doc, so that objects defined internally can
    appear in the public API, with all links to decorated objects going there.

    :param module: target module
    :return: decorated object
    """

    def decorated(func: T) -> T:
        func.__module__ = module
        return func

    return decorated
