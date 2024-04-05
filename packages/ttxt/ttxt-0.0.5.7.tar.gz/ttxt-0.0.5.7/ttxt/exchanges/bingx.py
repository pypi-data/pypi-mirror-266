import hmac
import base64
import hashlib
import json
import time
import requests
from datetime import datetime as dt
from ttxt.base import baseSpotExchange
from ttxt.types import baseTypes
from ttxt.utils import general

'''
kwards = {
    "category": "",
    "recv_window": ""
}
'''
class bingx(baseSpotExchange.BaseSpotExchange):
    def __init__(self, key, secret, **kwargs):
        super().__init__(key, secret, **kwargs)
        self.domain_url = "https://open-api.bingx.com"
        self.prefix = "/api/v4"
        self.category = kwargs["category"] if "category" in kwargs else "linear"
        self.recv_window = kwargs["recv_window"] if "recv_window" in kwargs else "5000"
        self.account_type = kwargs["account_type"] if "account_type" in kwargs else "UNIFIED"
        self.max_retries = 5
        self.symbolLotSize = {}

    def _getSymbol(self, symbol):
        return symbol.replace("/", "-")
    
    def _getUserSymbol(self, symbol):
        return symbol.replace("-", "/")
    
    ## Auth 
    def get_expire(self):
        return int((time.time() + 1) * 1000)  # websockets use seconds
    
    def generate_timestamp(self):
        """
        Return a millisecond integer timestamp.
        """
        return int(time.time() * 10**3)
    
    def _get_sign(self, payload):
        signature = hmac.new(self.secret.encode("utf-8"), payload.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()
        return signature
    
    def _parseParams(self, paramsMap):
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        return paramsStr+"&timestamp="+str(int(time.time() * 1000))

    def _send_request(self, method, path, params, payload):
        params = self._parseParams(params)
        url = "%s%s?%s&signature=%s" % (self.domain_url, path, params, self._get_sign(params))
        headers = {
            'X-BX-APIKEY': self.key,
        }
        try:
            response = requests.request(method, url, headers=headers, data=payload)
            return response.json()
        except Exception as e:
            raise e
        
    def _prepare_params(self, params):
        payload = "&".join(
                [
                    str(k) + "=" + str(v)
                    for k, v in sorted(params.items())
                    if v is not None
                ]
            )
        return payload

    def _unsignedRequest(self, method=None, path=None, query=None, auth=False):
        path = self.domain_url + path
        if query is None:
            query = {}
        # Store original recv_window.
        recv_window = self.recv_window
        # Bug fix: change floating whole numbers to integers to prevent
        # auth signature errors.
        if query is not None:
            for i in query.keys():
                if isinstance(query[i], float) and query[i] == int(query[i]):
                    query[i] = int(query[i])
        # Send request and return headers with body. Retry if failed.
        retries_attempted = self.max_retries
        req_params = None
        while True:
            retries_attempted -= 1
            if retries_attempted < 0:
                raise Exception(
                    "Bad Request. Retries exceeded maximum."
                )
            req_params = self._prepare_params(query)
            # Authenticate if we are using a private endpoint.
            headers = {}
            if method == "GET":
                try:
                    if req_params:
                        client = requests.Session()
                        r = client.prepare_request(requests.Request(method, path, headers=headers))
                        #esp = client.send(r, timeout=60) 
                        resp = requests.get(path + f"?{req_params}", headers=headers)
                    else:
                        r = requests.get(path, headers=headers)
                    return resp.json()
                except Exception as e:
                    raise e
            if method == "POST":
                r = requests.post( path, data=req_params, headers=headers)
                return r.json()
            if method == "DELETE":
                r = requests.delete( path, data=req_params, headers=headers)
                return r.json()

    ## parsers
    def _parseBalance(self, balData):
        if balData['code'] != 0: raise Exception(balData['msg'])
        parsedBal = {"free": {}, "total": {}}
        for balDataEle in balData['data']['balances']:
            parsedBal["free"][balDataEle["asset"]] = float(balDataEle["free"])
            parsedBal["total"][balDataEle["asset"]] = float(balDataEle["locked"]) + parsedBal["free"][balDataEle["asset"]]
        return parsedBal

    def _parseOrder(self, order):
        parsedOrder = {"id": None, "symbol": None, "price": None, "amount": None, 
                       "side": None, "timestamp": None, "status": None, "orderJson": None}
        parsedOrder["id"] = order["orderId"]
        parsedOrder["symbol"] = self._getUserSymbol(order["symbol"])
        parsedOrder["price"] = order["price"]
        parsedOrder["amount"] = order["origQty"]
        parsedOrder["side"] = order["side"].lower()
        parsedOrder["timestamp"] = order["time"]
        parsedOrder["status"] = order["status"]
        parsedOrder["orderJson"] = json.dumps(order)
        return parsedOrder
    
    '''
    {'code': 0, 'msg': '', 'debugMsg': '', 'data': {'symbol': 'GALA-USDT', 'orderId': 1765446279820824576, 'price': '0.04', 'stopPrice': '0', 
    'origQty': '100', 'executedQty': '0', 'cummulativeQuoteQty': '0', 'status': 'CANCELED', 'type': 'LIMIT', 'side': 'BUY'}}
    '''
    def _parseCancelOrder(self, order):
        if order['code'] != 0: raise Exception(order['msg'])
        order = order['data']
        parsedOrder = {"id": None, "symbol": None, "price": None, "amount": None, 
                       "side": None, "timestamp": None, "status": None, "orderJson": None}
        parsedOrder["id"] = order["orderId"]
        parsedOrder["symbol"] = self._getUserSymbol(order["symbol"])
        parsedOrder["price"] = order["price"]
        parsedOrder["amount"] = order["origQty"]
        parsedOrder["side"] = order["side"].lower()
        parsedOrder["status"] = order["status"]
        parsedOrder["orderJson"] = json.dumps(order)
        return parsedOrder
    
    def _parseCreateOrder(self, order):
        if order['code'] != 0: raise Exception(order['msg'])
        parsedOrder = {}
        order = order["data"]
        parsedOrder["id"] = order["orderId"]
        parsedOrder["symbol"] = self._getUserSymbol(order["symbol"])
        parsedOrder["price"] = order["price"]
        parsedOrder["amount"] = order["origQty"]
        parsedOrder["side"] = order["side"].lower()
        parsedOrder["timestamp"] = int(order["transactTime"])
        parsedOrder["status"] = order["status"]
        parsedOrder["orderJson"] = json.dumps(order)
        return parsedOrder

    def _parseOpenOrders(self, orders):
        if orders['code'] != 0: raise Exception(orders['msg'])
        parsedOrderList = []
        for order in orders["data"]["orders"]:
            parsedOrderList.append(self._parseOrder(order))
        return parsedOrderList
    
    def _parseTrades(self, trades):
        def parseTrade(trade):
            parsedTrade = {}
            parsedTrade["symbol"] = self._getUserSymbol(trade["symbol"])
            parsedTrade["id"] = trade.get("orderId", None)
            parsedTrade["tradeId"] = trade.get("id", None)
            parsedTrade["side"] = "buy" if trade["isBuyer"] else "sell"
            parsedTrade["price"] = trade.get("price", None)
            parsedTrade["amount"] = trade.get("qty", None)
            parsedTrade["takerOrMaker"] = "maker" if trade["isMaker"] else "taker"
            if "time" in trade:
                parsedTrade["timestamp"] = trade["time"]
                parsedTrade["datetime"] = general.ts_to_datetime(parsedTrade["timestamp"])
            else: 
                parsedTrade["timestamp"] = None
                parsedTrade["datetime"] = None
            parsedTrade["fee"] = trade.get("commission", None)
            parsedTrade["fee_currency"] = trade.get("commissionAsset", None)
            return parsedTrade
        if trades['code'] != 0: raise Exception(trades['msg'])
        parsedTradeList = []
        for trade in trades['data']['fills']:
            parsedTradeList.append(parseTrade(trade))
        return parsedTradeList


    def _parseFetchedOrder(self, order):
        pass

    ## Exchange functions 
    def create_order(self, symbol, type, side, amount, price=None, params={}):
        try:
            if type == "market":
                self.create_market_order(symbol, amount, side, params={})
            elif type == "limit":
                self.create_limit_order(symbol, amount, side, price, params={})
        except Exception as e:
            raise e
    
    def create_limit_order(self, symbol, amount, side, price, params={}):
        ticker = self._getSymbol(symbol)
        params = {
            "symbol": ticker,
            "side": side.upper(),
            "type": "LIMIT",
            "price": float(price),
            "quantity": float(amount),
            "timestamp": self.generate_timestamp()
        }
        params.update(params) 
        apiUrl = "/openApi/spot/v1/trade/order"
        response = self._send_request(method='POST', path=apiUrl, params=params, payload={})
        return self._parseCreateOrder(response)
    
    def create_market_order(self, symbol, amount, side, params={}):
        ticker = self._getSymbol(symbol)
        params = {
            "symbol": ticker,
            "side": side.upper(),
            "type": "MARKET",
            "quantity": float(amount),
            "timestamp": self.generate_timestamp()
        }
        params.update(params) 
        apiUrl = "/openApi/spot/v1/trade/order"
        response = self._send_request(method='POST', path=apiUrl, params=params, payload={})
        return self._parseCreateOrder(response)
    
    def fetch_order(self, id, symbol=None):
        apiUrl = "/openApi/spot/v1/trade/query"
        queryParams = {"orderId": id, "symbol": symbol}  # maybe have a set symbol function ?
        try:
            resp = resp = self._send_request(method='GET', path=apiUrl, params=queryParams, payload=None)
            return resp #self._parseOrder(resp)
        except Exception as e:
            raise e

    def fetch_open_orders(self, symbol=None,  kwargs=None):
        apiUrl = "/openApi/spot/v1/trade/openOrders"
        queryParams = {"timestamp": self.generate_timestamp()}
        try:
            resp = self._send_request(method='GET', path=apiUrl, params=queryParams, payload=None)
            return self._parseOpenOrders(resp)
        except Exception as e:
            raise e
        
    def cancel_order(self, id, symbol=None, params={}):
        apiUrl = "/openApi/spot/v1/trade/cancel"
        queryParams = {"orderId": id, "symbol": self._getSymbol(symbol)}
        try:
            resp = self._send_request(method='GET', path=apiUrl, params=queryParams, payload=None)
            return self._parseCancelOrder(resp)
        except Exception as e:
            raise e

    def fetch_ticker(self, symbol: str, params={}) -> baseTypes.Ticker:
        apiUrl = "/openApi/spot/v1/common/symbols"
        queryParams = {"symbol": self._getSymbol(symbol)}
        try:
            resp = self._unsignedRequest(method='GET', path=apiUrl, query=queryParams)
            return resp # parse this response into Ticker
        except Exception as e:
            raise e
    
    # params = {"startTime": 1702512246000, "endTime": 1702512248000, "limit": 100}
    def fetch_ohlcv(self, symbol, interval, params={}):
        apiUrl = "/openApi/spot/v2/market/kline"
        queryParams = {"symbol": self._getSymbol(symbol), "interval": interval}
        try:
            resp = self._unsignedRequest(method='GET', path=apiUrl, query=queryParams)
            return resp # parse this response into Ticker
        except Exception as e:
            raise e
    
    def fetch_balance(self, params={}) -> baseTypes.Balances:
        apiUrl = '/openApi/spot/v1/account/balance'
        queryParams = {}
        try:
            resp = self._send_request(method='GET', path=apiUrl, params=queryParams, payload=None)
            return self._parseBalance(resp)
        except Exception as e:
            raise e
        
    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        apiUrl = '/openApi/spot/v1/trade/myTrades'
        queryParams = {
            "symbol": self._getSymbol(symbol),
        }
        if since:
            queryParams["startTime"] = since
        if 'endTime' in params and params['endTime']:
                params['endTime'] = params['endTime']
        if limit:
            params['limit'] = limit
        try:
            resp = self._send_request(method='GET', path=apiUrl, params=queryParams, payload=None)
            return self._parseTrades(resp)
        except Exception as e:
            raise e