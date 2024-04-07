from __future__ import annotations

import copy
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Union

from glitter_proto.blockved.glitterchain.index import Argument as Argument_pb

from glitter_sdk.util.json import JSONSerializable

from .argument import Argument


class Arguments():
    """Represents an unordered collection of :class:`Argument` objects

    Args:
        arg (Optional[Arguments.Input], optional): argument to convert.

    Raises:
        TypeError: if ``arg`` is not an Iterable
    """

    Input = Union[List[Argument_pb]]
    """Types which can be converted into a :class:`Arguments` object."""

    arguments: List[Argument_pb]

    def __init__(self, arg: Optional[Arguments.Input] = None, **denoms):
        """Converts the argument into a :class:`Arguments` object."""

        if arg is None:
            self.arguments = []
            return

        if isinstance(arg, Arguments):
            self.arguments = copy.deepcopy(arg.arguments)
            return

        if isinstance(arg, list):
            self.arguments = [item for item in arg]
        else:
            x = type(arg)
            print(x)

    @classmethod
    def from_proto(cls, proto: List[Argument_pb]) -> Arguments:
        """Converts list of Argument-data objects to :class:`Arguments`.

        Args:
            data (list): list of Argument-data objects
        """
        return cls(proto)

    def to_proto(self) -> List[Argument_pb]:
        return [item.to_proto() for item in self]

    def append(self, ob: Union[Argument_pb, Arguments]) -> None:
        if isinstance(ob, Argument_pb):
            self.arguments.append(ob)
        if isinstance(ob, Arguments):
            for item in ob.arguments:
                self.arguments.append(item)

    def to_list(self) -> List[Argument_pb]:
        return self.arguments

    def __iter__(self):
        return iter(self.to_list())
