from __future__ import annotations

from typing import Union

from pydantic import StrictBool, StrictFloat, StrictInt, StrictStr

from kelvin.krn import KRNAssetDataStream
from kelvin.message.message import Message
from kelvin.message.msg_type import KMessageTypeData, KMessageTypeParameter


class AssetDataMessage(Message):
    resource: KRNAssetDataStream


class Number(AssetDataMessage):
    _TYPE = KMessageTypeData("number")

    payload: Union[StrictFloat, StrictInt] = 0.0


class String(AssetDataMessage):
    _TYPE = KMessageTypeData("string")

    payload: StrictStr = ""


class Boolean(AssetDataMessage):
    _TYPE = KMessageTypeData("boolean")

    payload: StrictBool = False


class NumberParameter(Message):
    _TYPE = KMessageTypeParameter("number")

    payload: Union[StrictFloat, StrictInt] = 0.0


class StringParameter(Message):
    _TYPE = KMessageTypeParameter("string")

    payload: StrictStr = ""


class BooleanParameter(Message):
    _TYPE = KMessageTypeParameter("boolean")

    payload: StrictBool = False
