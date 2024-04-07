from __future__ import annotations

import attr
from glitter_proto.blockved.glitterchain.index import Argument as Argument_pb
from glitter_proto.blockved.glitterchain.index import ArgumentVarType as ArgumentVarType_pb
from glitter_sdk.util.json import JSONSerializable



@attr.s(frozen=True)
class Argument(JSONSerializable):
    """Represents a (type, value) pairing
    """
    type: ArgumentVarType_pb = attr.ib()

    value: bytes = attr.ib()  # type: ignore
    """Argument's value -- can be a ``int`` or :class:`Dec`"""

    @classmethod
    def from_proto(cls, proto: Argument_pb) -> Argument:
        return cls(proto.type, proto.value)

    def to_proto(self) -> Argument_pb:
        argument = Argument_pb()
        argument.type = self.type
        argument.value = self.value
        return argument
