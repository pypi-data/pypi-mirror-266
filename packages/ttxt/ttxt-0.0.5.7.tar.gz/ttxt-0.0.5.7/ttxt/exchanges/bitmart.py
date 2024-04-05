from enum import Enum, unique
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

@unique
class Auth(Enum):
    NONE = 1
    KEYED = 2
    SIGNED = 3

# memo = UID => password
class bitmart(baseSpotExchange.BaseSpotExchange):
    def __init__(self, key, secret, password, **kwargs):
        super().__init__(key, secret, **kwargs)
        self.password = password
        self.domain_url = 'https://api-cloud.bitmart.com'  # host + prefix
        # http header
        self.CONTENT_TYPE = 'Content-Type'
        self.USER_AGENT = 'User-Agent'
        self.X_BM_KEY = 'X-BM-KEY'
        self.X_BM_SIGN = 'X-BM-SIGN'
        self.X_BM_TIMESTAMP = 'X-BM-TIMESTAMP'
        self.__version__ = "1.0.1"
        # http header
        self.APPLICATION_JSON = 'application/json'
        self.VERSION = 'bitmart-python-sdk-api/'
        self.GET = "GET"
        self.POST = "POST"
        self.DELETE = "DELETE"
        self.TIMEOUT = (5,10)

    def _getSymbol(self, symbol):
        return symbol.replace("/", "_")
    
    def _getUserSymbol(self, symbol):
        return symbol.replace("_", "/")

    ## Auth 
    def sign(self, message):
        mac = hmac.new(bytes(self.secret, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        return mac.hexdigest()

    # timestamp + "#" + memo + "#" + queryString
    def pre_substring(self, timestamp, body):
        return f'{str(timestamp)}#{self.password}#{body}'

    def get_header(self, sign, timestamp):
        header = dict()
        header[self.CONTENT_TYPE] = self.APPLICATION_JSON
        header[self.USER_AGENT] = self.VERSION + self.__version__

        if self.key:
            header[self.X_BM_KEY] = self.key
        if sign:
            header[self.X_BM_SIGN] = sign
        if timestamp:
            header[self.X_BM_TIMESTAMP] = str(timestamp)

        return header

    def parse_params_to_str(self, params):
        url = '?'
        for key, value in params.items():
            url = url + str(key) + '=' + str(value) + '&'

        return url[0:-1]

    def get_timestamp(self):
        return str(datetime.datetime.now().timestamp() * 1000).split('.')[0]

    ## Requests 
    def _signedRequest(self, method, request_path, params, auth):
        if method == self.GET or method == self.DELETE:
            url = self.domain_url + request_path + self.parse_params_to_str(params)
        else:
            url = self.domain_url + request_path

        # set body
        body = json.dumps(params) if method == self.POST else ""

        # set header
        if auth == Auth.NONE:
            header = self.get_header(sign=None, timestamp=None)
        elif auth == Auth.KEYED:
            header = self.get_header(sign=None, timestamp=None)
        else:
            timestamp = self.get_timestamp()
            sign = self.sign(self.pre_substring(timestamp, str(body)))
            header = self.get_header(sign, timestamp)

        # send request
        response = None
        if method == self.GET:
            response = requests.get(url, headers=header, timeout=self.TIMEOUT)
        elif method == self.POST:
            response = requests.post(url, data=body, headers=header, timeout=self.TIMEOUT)
        elif method == self.DELETE:
            response = requests.delete(url, headers=header, timeout=self.TIMEOUT)

        # exception handle
        if not str(response.status_code) == '200':
            raise Exception(response)
        try:
            res_header = response.headers
            r = dict()
            try:
                r['Remaining'] = res_header['X-BM-RateLimit-Remaining']
                r['Limit'] = res_header['X-BM-RateLimit-Limit']
                r['Reset'] = res_header['X-BM-RateLimit-Reset']
            except:
                pass
            return response.json()

        except ValueError:
            raise Exception('Invalid Response: %s' % response.text)

    ## parsers
    def _parseBalance(self, balData):
        parsedBal = {"free": {}, "total": {}}
        if balData['code'] != 1000: raise Exception(balData['message'])
        for bal in balData['data']['wallet']:
            parsedBal["free"][bal["currency"]] = float(bal["available"])
            parsedBal["total"][bal["currency"]] = float(bal['frozen']) + parsedBal["free"][bal["currency"]]
        return parsedBal
    
    def _parseCreateOrder(self, orderData):
        parsedOrder = {}
        if orderData['code'] != 1000: raise Exception(orderData['message'])
        parsedOrder["orderId"] = orderData["data"]["order_id"]
        parsedOrder["symbol"] = None
        parsedOrder["price"] = None
        parsedOrder["amount"] = None
        parsedOrder["side"] = None
        parsedOrder["timestamp"] = None
        parsedOrder["status"] = None
        parsedOrder["orderJson"] = json.dumps(orderData)
        return parsedOrder
    
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
    
    def _parseOrder(self, order):
        parsedOrder = {}
        parsedOrder["id"] = order.get('orderId', None)
        parsedOrder["symbol"] = self._getUserSymbol(order["symbol"]) if "symbol" in order else None
        parsedOrder["price"] = float(order["price"]) if "price" in order else None 
        parsedOrder["amount"] = float(order["size"]) if "size" in order else None
        parsedOrder["side"] = order.get('side', None)
        parsedOrder["timestamp"] = int(float(order["createTime"])) if "createTime" in order else None
        parsedOrder["status"] = order.get('state', None)
        parsedOrder["orderJson"] = json.dumps(order) if order else None 
        return parsedOrder
    
    def _parseOpenOrders(self, orders):
        if orders['code'] != 1000: raise Exception(orders['message'])
        parsedOrderList = []
        for order in orders["data"]:
            parsedOrderList.append(self._parseOrder(order))
        return parsedOrderList

    # cancel request doesnt return an order id in response
    def _parseCancelOrder(self, order):
        if order['code'] != 1000: raise Exception(order['message'])
        return order['data']
    
    def _parseTrades(self, trades):
        def parseTrade(trade):
            parsedTrade = {}
            parsedTrade["id"] = trade.get("orderId", None)
            parsedTrade["tradeId"] = trade.get("tradeId", None)
            parsedTrade["side"] = trade.get("side", None)
            parsedTrade["price"] = trade.get("price", None)
            parsedTrade["amount"] = trade.get("size", None)
            parsedTrade["symbol"] = self._getUserSymbol(trade["symbol"])
            parsedTrade["takerOrMaker"] = trade.get("tradeRole", None)
            if "updateTime" in trade:
                parsedTrade["timestamp"] = int(trade["updateTime"])
                parsedTrade["datetime"] = general.ts_to_datetime(parsedTrade["timestamp"])
            else: 
                parsedTrade["timestamp"] = None
                parsedTrade["datetime"] = None
            return parsedTrade
        parsedTradeList = []
        if trades['code'] != 1000: raise Exception(trades['message'])
        for trade in trades['data']:
            parsedTradeList.append(parseTrade(trade))
        return parsedTradeList

    ## Exchange functions 

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        try:
            if type == "market":
                body = {
                    'symbol': self._getSymbol(symbol),
                    'side': side,
                    'type': 'market',
                    'size': amount,
                    'notional': amount
                }
            elif type == "limit":
                body = {
                    'symbol': self._getSymbol(symbol),
                    'side': side,
                    'type': 'limit',
                    'size': amount,
                    'price': price,
                }
            body.update(params)
            apiUrl = f"/spot/orders"
            resp = self._signedRequest(method='POST', request_path=apiUrl, params=body, auth=Auth.SIGNED)
            return self._parseCreateOrder(resp)
        except Exception as e:
            raise e
        
    def create_limit_order(self, symbol, amount, side, price, params={}):
        body = {
            'symbol': self._getSymbol(symbol),
            'side': side,
            'type': 'limit',
            'size': amount,
            'price': price,
        }
        body.update(params)
        apiUrl = f"/spot/v2/submit_order"
        try:
            resp = self._signedRequest(method='POST', request_path=apiUrl, params=body, auth=Auth.SIGNED)
            return self._parseCreateOrder(resp)
        except Exception as e:
            raise e

    def create_market_order(self, symbol, amount, side, params={}):
        body = {
            'symbol': self._getSymbol(symbol),
            'side': side,
            'type': 'market',
            'size': amount,
            'notional': amount
        }
        body.update(params)
        apiUrl = f"/spot/v2/submit_order"
        apiUrl = f"/spot/v2/submit_order"
        try:
            resp = self._signedRequest(method='POST', request_path=apiUrl, params=body, auth=Auth.SIGNED)
            return self._parseCreateOrder(resp)
        except Exception as e:
            raise e
    
    def fetch_order(self, id, symbol=None):
        raise NotImplementedError("method not implemented")

    def fetch_open_orders(self, symbol=None,  kwargs=None):
        apiUrl = "/spot/v4/query/open-orders"
        body = {}
        if symbol:
            body['symbol'] = self._getSymbol(symbol)
        try:
            resp = self._signedRequest(method='POST', request_path=apiUrl, params=body, auth=Auth.SIGNED)
            return self._parseOpenOrders(resp)
        except Exception as e:
            raise e
        
    def cancel_order(self, id, symbol=None):
        apiUrl = "/spot/v3/cancel_order"
        body = {
            "symbol": self._getSymbol(symbol),
            "order_id": id
        }
        try:
            resp = self._signedRequest(method='POST', request_path=apiUrl, params=body, auth=Auth.SIGNED)
            return self._parseCancelOrder(resp)
        except Exception as e:
            raise e

    def fetch_ticker(self, symbol: str, params={}) -> baseTypes.Ticker:
        raise NotImplementedError("method not implemented")
    
    def fetch_balance(self, params={}) -> baseTypes.Balances:
        apiUrl = '/account/v1/wallet'
        try:
            resp = self._signedRequest(method='GET', request_path=apiUrl, params=params, auth=Auth.KEYED)
            return self._parseBalance(resp)
        except Exception as e:
            raise e
        
    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        apiUrl = '/spot/v4/query/trades'
        if symbol:
            params['symbol'] = self._getSymbol(symbol)
        if limit:
            params['limit'] = limit
        if since:
            params['startTime'] = int(since)
        try:
            resp = self._signedRequest(method='POST', request_path=apiUrl, params=params, auth=Auth.SIGNED)
            return self._parseTrades(resp)
        except Exception as e:
            raise e
        
    def fetch_order_book(self, symbol: str, limit=None, params={}) -> baseTypes.OrderBook:
        raise NotImplementedError("method not implemented")
    
    # parsed OHLCV = [[ts_ms, o, h ,l ,c, v],[]]
    def fetch_ohlcv(self, symbol: str, timeframe='1m', since = None, limit = None, params={}):
        raise NotImplementedError("method not implemented")