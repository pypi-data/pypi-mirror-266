from ttxt.base import baseFuturesExchange, baseSpotExchange
from ttxt.exchanges.gateFutures import gateFutures
from ttxt.exchanges.bybitFutures import bybitFutures
from ttxt.exchanges.bitgetFutures import bitgetFutures
from ttxt.exchanges.bingx import bingx
from ttxt.exchanges.biconomy import biconomy
from ttxt.exchanges.mexc import mexc
from ttxt.exchanges.gateio import gateio
from ttxt.exchanges.bybit import bybit
from ttxt.exchanges.okx import okx
from ttxt.exchanges.huobi import huobi
from ttxt.exchanges.bitmart import bitmart
from ttxt.exchanges.cryptocom import cryptocom
from ttxt.exchanges.bitget import bitget
from ttxt.exchanges.binance import binance
from ttxt.exchanges.kucoin import kucoin

exchanges = [
    "biconomy",
    "binance",
    "bingx",
    "bitgetFutures",
    "bitget",
    "bybitFutures",
    "gateFutures",
    "kucoin"
    "mexc",
    "gateio",
    "bybit",
    "okx",
    "huobi",
    "bitmart",
    "cryptocom"
]

base = [
    "baseFuturesExchange",
    "baseSpotExchange"
]

_all__ =  exchanges + base