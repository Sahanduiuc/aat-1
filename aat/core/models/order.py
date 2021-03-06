from pydantic import validator
from typing import Mapping, Union, Type
from .data import Data
from ...config import DataType, OrderFlag, OrderType, Side
from ..exchange import ExchangeType
from ...common import _in_cpp


try:
    from aat.binding import OrderCpp
    _CPP = _in_cpp()
except ImportError:
    _CPP = False


def _make_cpp_order(id, timestamp, volume, price, side, instrument, exchange=ExchangeType(""), filled=0.0, order_type=OrderType.LIMIT, flag=OrderFlag.NONE, stop_target=None, notional=0.0):
    '''helper method to ensure all arguments are setup'''
    return OrderCpp(id, timestamp, volume, price, side, instrument, exchange, filled, order_type, flag, stop_target, notional)


class Order(Data):
    def __new__(cls, *args, **kwargs):
        if _CPP:
            return _make_cpp_order(*args, **kwargs)
        return super(Order, cls).__new__(cls)

    # for convenience
    Types = OrderType
    Sides = Side
    Flags = OrderFlag

    # Values
    type: DataType = DataType.ORDER
    order_type: OrderType = OrderType.LIMIT
    flag: OrderFlag = OrderFlag.NONE
    filled: float = 0.0
    stop_target: Union[Data, None] = None
    notional: float = 0.0

    @validator("type")
    def _assert_type_is_order(cls, v):
        assert v == DataType.ORDER
        return v

    @validator("stop_target")
    def _assert_stop_target_not_stop(cls, v, values, **kwargs):
        assert isinstance(v, Order)
        assert v.order_type != OrderType.STOP
        return v

    @validator("notional")
    def _assert_notional_set_correct(cls, v, values, **kwargs) -> float:
        if values['order_type'] == OrderType.MARKET:
            return v
        return values['price'] * values['volume']

    def __str__(self):
        return f'<{self.instrument}-{self.volume}@{self.price}-{self.exchange}-{self.side}>'

    def to_json(self) -> Mapping[str, Union[str, int, float]]:
        return \
            {'id': self.id,
             'timestamp': self.timestamp,
             'volume': self.volume,
             'price': self.price,
             'side': self.side.value,
             'instrument': str(self.instrument),
             'exchange': str(self.exchange)}

    @staticmethod
    def perspectiveSchema() -> Mapping[str, Type]:
        return {
            "id": int,
            "timestamp": int,
            "volume": float,
            "price": float,
            "side": str,
            "instrument": str,
            "exchange": str,
        }
