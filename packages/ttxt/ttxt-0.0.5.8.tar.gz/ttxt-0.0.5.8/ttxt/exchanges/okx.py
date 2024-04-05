import hmac
import base64
import hashlib
import json
import time
import requests
import datetime
from ttxt.base import baseSpotExchange
from ttxt.types import baseTypes
from ttxt.utils import general


class okx(baseSpotExchange.BaseSpotExchange):
    def __init__(self, key, secret, password, **kwargs):
        super().__init__(key, secret, **kwargs)
        self.password = password
        self.domain = "https://www.okx.com"
        ## constants
        self.CONTENT_TYPE = 'Content-Type'
        self.OK_ACCESS_KEY = 'OK-ACCESS-KEY'
        self.OK_ACCESS_SIGN = 'OK-ACCESS-SIGN'
        self.OK_ACCESS_TIMESTAMP = 'OK-ACCESS-TIMESTAMP'
        self.OK_ACCESS_PASSPHRASE = 'OK-ACCESS-PASSPHRASE'
        self.APPLICATION_JSON = 'application/json'
        self.GET = "GET"
        self.POST = "POST"

    def _getSymbol(self, symbol):
        return symbol.replace("/", "-")
    
    def _getUserSymbol(self, symbol):
        return symbol.replace("-", "/")

    ## Auth 
    def sign(self, message):
        mac = hmac.new(bytes(self.secret, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d)


    def pre_hash(self, timestamp, method, request_path, body):
        return str(timestamp) + str.upper(method) + request_path + body


    def get_header(self, sign, timestamp):
        header = dict()
        header[self.CONTENT_TYPE] = self.APPLICATION_JSON
        header[self.OK_ACCESS_KEY] = self.key
        header[self.OK_ACCESS_SIGN] = sign
        header[self.OK_ACCESS_TIMESTAMP] = str(timestamp)
        header[self.OK_ACCESS_PASSPHRASE] = self.password
        # header['x-simulated-trading'] = flag
        return header

    def get_header_no_sign(self):
        header = dict()
        header[self.CONTENT_TYPE] = self.APPLICATION_JSON
        # header['x-simulated-trading'] = flag
        return header

    def parse_params_to_str(self, params):
        url = '?'
        for key, value in params.items():
            if(value != ''):
                url = url + str(key) + '=' + str(value) + '&'
        url = url[0:-1]
        return url

    def get_timestamp(self):
        now = datetime.datetime.utcnow()
        t = now.isoformat("T", "milliseconds")
        return t + "Z"

    def signature(self, timestamp, method, request_path, body):
        if str(body) == '{}' or str(body) == 'None':
            body = ''
        message = str(timestamp) + str.upper(method) + request_path + str(body)

        mac = hmac.new(bytes(self.secret, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        d = mac.digest()

        return base64.b64encode(d)

    ## Requests 
    def _signedRequest(self, method, request_path, params):
        if method == "GET":
            request_path = request_path + self.parse_params_to_str(params)
        timestamp = self.get_timestamp()
        body = json.dumps(params) if method == "POST" else ""
        if self.key != '-1':
            sign = self.sign(self.pre_hash(timestamp, method, request_path, str(body)))
            header = self.get_header(sign, timestamp)
        else:
            header = self.get_header_no_sign()
        response = None
        url = self.domain + request_path
        if method == "GET":
            response = requests.get(url, headers=header)
        elif method == "POST":
            response = requests.post(url, data=body, headers=header)
        return response.json()
    
    ## parsers
    def _parseBalance(self, balData):
        if balData['code'] != "0": raise Exception(balData["msg"])
        parsedBal = {"free": {}, "total": {}}
        for bal in balData["data"][0]["details"]:
            parsedBal["free"][bal["ccy"]] = bal.get("availBal", None)
            parsedBal["total"][bal["ccy"]] = bal.get("eq", None)
        return parsedBal
    
    def _parseOrderbook(self, orderbookData):
        parsedData = {}
        parsedData["datetime"] = None
        parsedData["timestamp"] = orderbookData.get("current", None)
        parsedData["nonce"] = orderbookData.get("id", None)
        if "bids" in orderbookData:
            parsedData["bids"] = [[float(d[0]), float(d[1])] for d in orderbookData["bids"]]
        else: parsedData["bids"] = []
        if "asks" in orderbookData:
            parsedData["asks"] = [[float(d[0]), float(d[1])] for d in orderbookData["asks"]]
        else: parsedData["asks"] = []
        return parsedData

    def _parseCreateOrder(self, order):
        parsedOrder = {}
        if order['code'] != "0": raise Exception(order["msg"])
        parsedOrder["id"] = order['data'][0]['ordId']
        parsedOrder["symbol"] = None
        parsedOrder["price"] = None
        parsedOrder["amount"] = None
        parsedOrder["side"] = None
        parsedOrder["timestamp"] = float(order["outTime"]) if "outTime" in order else None
        parsedOrder["status"] = None
        parsedOrder["orderJson"] = json.dumps(order) if order else None 
        return parsedOrder
    
    def _parseOrder(self, order):
        parsedOrder = {}
        parsedOrder["id"] = order.get('ordId', None)
        parsedOrder["symbol"] = self._getUserSymbol(order["instId"]) if "instId" in order else None
        parsedOrder["price"] = float(order["px"]) if "px" in order else None 
        parsedOrder["amount"] = float(order["sz"]) if "sz" in order else None
        parsedOrder["side"] = order.get('side', None)
        parsedOrder["timestamp"] = float(order["cTime"]) if "cTime" in order else None
        parsedOrder["status"] = order["status"] if "status" in order else None
        parsedOrder["orderJson"] = json.dumps(order) if order else None 
        return parsedOrder

    def _parseOpenOrders(self, orders):
        parsedOrderList = []
        if order['code'] != "0": raise Exception(order["msg"])
        for order in orders['data']:
            parsedOrderList.append(self._parseOrder(order))
        return parsedOrderList
    
    def _parseTrades(self, trades):
        def parseTrade(trade):
            parsedTrade = {}
            parsedTrade["symbol"] = trade.get('instId', None)
            parsedTrade["id"] = trade.get("ordId", None)
            parsedTrade["tradeId"] = trade.get("tradeId", None)
            parsedTrade["side"] = trade.get("side", None)
            parsedTrade["price"] = trade.get("fillPx", None)
            parsedTrade["amount"] = trade.get("fillSz", None)
            parsedTrade["takerOrMaker"] = "taker" if trade['execType'] == 'T' else "maker"
            if "fillTime" in trade:
                parsedTrade["timestamp"] = int(float(trade["fillTime"]))
                parsedTrade["datetime"] = general.ts_to_datetime(parsedTrade["timestamp"])
            else: 
                parsedTrade["timestamp"] = None
                parsedTrade["datetime"] = None
            parsedTrade["feeCurrency"] = trade["feeCcy"]
            parsedTrade["fee"] = trade["fee"]
            return parsedTrade
        parsedTradeList = []
        if trades['code'] != "0": raise Exception(trades["msg"])
        for trade in trades["data"]:
            parsedTradeList.append(parseTrade(trade))
        return parsedTradeList

    ## Exchange functions 

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == "market":
            body = {
                "tdMode": "cash",
                "instId": self._getSymbol(symbol),
                "ordType": "market",
                "side": side,
                "iceberg": params["iceberg"] if "iceberg" in params else "0",
                "sz": str(amount)
            }
        elif type == "limit":
            body = {
                "tdMode": "cash",
                "instId": self._getSymbol(symbol),
                "ordType": "limit",
                "side": side,
                "iceberg": params["iceberg"] if "iceberg" in params else "0",
                "sz": str(amount),
                "px": str(price)
            }
        apiUrl = f"/api/v5/trade/order"
        try:
            response = self._signedRequest(method='POST', request_path=apiUrl, params=body)
            return self._parseCreateOrder(response)
        except Exception as e:
            raise e
        
    def create_limit_order(self, symbol, amount, side, price, params={}):
        body = {
            "tdMode": "cash",
            "instId": self._getSymbol(symbol),
            "ordType": "limit",
            "side": side,
            "iceberg": params["iceberg"] if "iceberg" in params else "0",
            "sz": str(amount),
            "px": str(price)
        }
        apiUrl = f"/api/v5/trade/order"
        try:
            response = self._signedRequest(method='POST', request_path=apiUrl, params=body)
            return self._parseCreateOrder(response)
        except Exception as e:
            raise e

    def create_market_order(self, symbol, amount, side, params={}):
        body = {
            "tdMode": "cash",
            "instId": self._getSymbol(symbol),
            "ordType": "market",
            "side": side,
            "iceberg": params["iceberg"] if "iceberg" in params else "0",
            "sz": str(amount)
        }
        apiUrl = f"/api/v5/trade/order"
        try:
            response = self._signedRequest(method='POST', request_path=apiUrl, params=body)
            return self._parseCreateOrder(response)
        except Exception as e:
            raise e
    
    def fetch_order(self, id, symbol=None):
        raise NotImplementedError("method not implemented")

    def fetch_open_orders(self, symbol=None,  kwargs=None):
        apiUrl = "/api/v5/trade/orders-pending"
        params = {"instId": self._getSymbol(symbol), "instType": "SPOT"}
        try:
            response = self._signedRequest(method='GET', request_path=apiUrl, params=params)
            return self._parseOpenOrders(response)
        except Exception as e:
            raise e
        
    def cancel_order(self, id, symbol=None):
        apiUrl = "/api/v5/trade/cancel-order"
        params = {"instId": self._getSymbol(symbol), "ordId": id}
        try:
            response = self._signedRequest(method='POST', request_path=apiUrl, params=params)
            return self._parseCreateOrder(response)
        except Exception as e:
            raise e

    def fetch_ticker(self, symbol: str, params={}) -> baseTypes.Ticker:
        raise NotImplementedError("method not implemented")
    
    def fetch_balance(self, params={}) -> baseTypes.Balances:
        apiUrl = '/api/v5/account/balance'
        try:
            resp = self._signedRequest(method='GET', request_path=apiUrl, params=params)
            return self._parseBalance(resp)
        except Exception as e:
            raise e
    
    # for extra params: https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-transaction-details-last-3-months
    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        apiUrl = '/api/v5/trade/fills-history'
        if symbol:
            params['instType'] = "SPOT"
        if limit:
            params['limit'] = limit
        if since:
            params['begin'] = int(since)
        try:
            resp = self._signedRequest(method='GET', request_path=apiUrl, params=params)
            return self._parseTrades(resp)
        except Exception as e:
            raise e
        
    def fetch_order_book(self, symbol: str, limit=None, params={}) -> baseTypes.OrderBook:
        raise NotImplementedError("method not implemented")
    
    # parsed OHLCV = [[ts_ms, o, h ,l ,c, v],[]]
    def fetch_ohlcv(self, symbol: str, timeframe='1m', since = None, limit = None, params={}):
        raise NotImplementedError("method not implemented")