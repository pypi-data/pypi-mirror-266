from kelvin.application.filters import is_data_message
from kelvin.krn import KRNAssetDataStream
from kelvin.message import Number, NumberParameter


def test_is_data_message():
    assert is_data_message(Number(payload=1.0, resource=KRNAssetDataStream("foo", "bar")))
    assert is_data_message(NumberParameter(payload=1.0, resource=KRNAssetDataStream("foo", "bar"))) is False
