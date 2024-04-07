"""Bank module message types."""

from __future__ import annotations

from typing import List

from betterproto.lib.google.protobuf import Any as Any_pb
from glitter_proto.cosmos.bank.v1beta1 import Input as Input_pb
from glitter_proto.cosmos.bank.v1beta1 import MsgMultiSend as MsgMultiSend_pb
from glitter_proto.blockved.glitterchain.index import SqlExecRequest as SQLExecRequest_pb
from glitter_proto.blockved.glitterchain.index import SqlGrantRequest as SQLGrantRequest_pb
from glitter_proto.cosmos.bank.v1beta1 import Output as Output_pb

from glitter_sdk.core import AccAddress
from glitter_sdk.core.msg import Msg
from glitter_sdk.util.json import JSONSerializable
from .arguments import Arguments

__all__ = ["SQLExecRequest", "SQLGrantRequest"]

import attr


@attr.s
class SQLExecRequest(Msg):
    """Sends sql request.

    Args:
        uid (AccAddress): sender
        sql (AccAddress): recipient
        arguments (Arguments): arguments to send
    """

    type_amino = "cosmos-sdk/SQLExecRequest"
    """"""
    type_url = "/blockved.glitterchain.index.SQLExecRequest"
    """"""
    action = "send"
    """"""
    prototype = SQLExecRequest_pb
    """"""

    uid: AccAddress = attr.ib()
    sql: AccAddress = attr.ib()
    arguments: Arguments = attr.ib(converter=Arguments, default=None)

    @classmethod
    def from_proto(cls, proto: SQLExecRequest_pb) -> SQLExecRequest:
        return cls(
            uid=proto.uid,
            sql=proto.sql,
            arguments=Arguments.from_proto(proto.arguments)
        )

    def to_proto(self) -> SQLExecRequest_pb:
        proto = SQLExecRequest_pb()
        proto.uid = self.uid
        proto.sql = self.sql
        proto.arguments = [c for c in self.arguments]
        return proto


@attr.s
class SQLGrantRequest(Msg):
    """Grant ``role`` to ``to_u_i_d`` .

    Args:
        uid (AccAddress): sender
        to_uid (AccAddress): recipient
        role (str): role
        on_database (str): database
        on_table (str): table
    """

    type_amino = "cosmos-sdk/SQLGrantRequest"
    """"""
    type_url = "/blockved.glitterchain.index.SQLGrantRequest"
    """"""
    action = "send"
    """"""
    prototype = SQLGrantRequest_pb
    """"""

    uid: AccAddress = attr.ib()
    to_uid: AccAddress = attr.ib()
    role: AccAddress = attr.ib()
    on_database: AccAddress = attr.ib()
    on_table: AccAddress = attr.ib(default=None)

    @classmethod
    def from_proto(cls, proto: SQLGrantRequest_pb) -> SQLGrantRequest:
        return cls(
            uid=proto.uid,
            to_uid=proto.to_uid,
            role=proto.role,
            on_database=proto.on_database,
            on_table=proto.on_table,
        )

    def to_proto(self) -> SQLGrantRequest_pb:
        proto = SQLGrantRequest_pb()
        proto.uid = self.uid
        proto.to_uid = self.to_uid
        proto.role = self.role
        proto.on_database = self.on_database
        proto.on_table = self.on_table
        return proto
