"""Utility functionality used within `e2e.pom`

Classes, functions, and objects within this file should ideally be usable
outside of `e2e.pom`, as a test of fitness for this file. If it is specific to
`e2e.pom`, it belongs elsewhere.
"""
from typing import Any
from typing import List
from typing import Type
from typing import TypeVar

T = TypeVar("T")


def fqualname_of(obj: Any) -> str:
    """Gets the fully-qualified name for the given object."""
    return "{}.{}".format(obj.__class__.__module__, obj.__class__.__qualname__)


def fname_of(obj: Any) -> str:
    """Get the module-qualified path for the class.

    This will not properly communicate nested classes, functions, etc.
    """
    return "{}.{}".format(obj.__class__.__module__, obj.__class__.__name__)


def subclasses_of(cls: Type[T]) -> List[Type[T]]:
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(subclasses_of(subclass))

    return all_subclasses


# TODO: contextmanager timer
# def timer():
#     raise NotImplementedError
