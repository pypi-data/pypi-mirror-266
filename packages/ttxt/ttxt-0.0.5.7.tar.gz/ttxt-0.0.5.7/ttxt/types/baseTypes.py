import sys
import types
from typing import Union, List, Optional, Any
from decimal import Decimal


if sys.version_info.minor >= 8:
    from typing import TypedDict, Literal, Dict
else:
    from typing import Dict
    from typing_extensions import Literal
    TypedDict = Dict

if sys.version_info.minor >= 11:
    from typing import NotRequired
else:
    from typing_extensions import NotRequired

IndexType = Union[str, int]
Num = Union[None, str, float, int, Decimal]
Str = Optional[str]
Strings = Optional[List[str]]
Int = Optional[int]
Bool = Optional[bool]
MarketType = Literal['spot', 'margin', 'swap', 'future', 'option']
Numeric = Union[None, str, float, int, Decimal]
String = Optional[str]

class Ticker(TypedDict):
    info: Dict[str, Any]
    symbol: Str
    timestamp: Int
    datetime: Str
    high: Num
    low: Num
    bid: Num
    bidVolume: Num
    ask: Num
    askVolume: Num
    vwap: Num
    open: Num
    close: Num
    last: Num
    previousClose: Num
    change: Num
    percentage: Num
    average: Num
    quoteVolume: Num
    baseVolume: Num

class Balance(TypedDict):
    free: Num
    total: Num
    unrealisedPnl: Num
    currency: Str

class Balances(Dict[str, Balance]):
    datetime: Str
    timestamp: Int

class OrderBook(TypedDict):
    asks: List[Numeric]  # [[price, amount], []...]
    bids: List[Numeric]  # [[price, amount], []...]
    datetime: String
    timestamp: Int
    nonce: Int