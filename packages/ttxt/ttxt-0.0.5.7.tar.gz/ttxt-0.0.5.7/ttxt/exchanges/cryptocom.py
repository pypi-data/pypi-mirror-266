import hmac
import base64
import hashlib
import json
import time
import requests
from ttxt.base import baseSpotExchange
from ttxt.types import baseTypes
from ttxt.utils import general


class cryptocom(baseSpotExchange.BaseSpotExchange):
    def __init__(self, key, secret, **kwargs):
        super().__init__(key, secret, **kwargs)
        self.domain_url = "https://api.crypto.com/v2/" #https://api.crypto.com/exchange/v1/"
        self.MAX_LEVEL = 3

    def _getSymbol(self, symbol):
        return symbol.replace("/", "_")
    
    def _getUserSymbol(self, symbol):
        return symbol.replace("_", "/")

    ## Auth 
    def params_to_str(self, obj, level):
        if level >= self.MAX_LEVEL:
            return str(obj)

        return_str = ""
        for key in sorted(obj):
            return_str += key
            if obj[key] is None:
                return_str += 'null'
            elif isinstance(obj[key], list):
                for subObj in obj[key]:
                    return_str += self.params_to_str(subObj, level + 1)
            else:
                return_str += str(obj[key])
        return return_str
    
    def gen_sign(self, payload_str):
        return hmac.new(bytes(str(self.secret), 'utf-8'), msg=bytes(payload_str, 'utf-8'), digestmod=hashlib.sha256).hexdigest()

    def request_builder(self, params, payload_str, request_path, id, nonce):
        return json.dumps({
            "id": id,
            "method": request_path,
            "api_key": self.key,
            "params": params,
            "nonce": nonce,
            "sig": self.gen_sign(payload_str)
        })

    # def req_param_builder(self, param_str):


    ## Requests 
    def _signedRequest(self, request_path, method, params):
        common_headers = {'Content-Type': 'application/json'}
        if method == "POST":
            try:
                reqId, nonce = general.get_random_int(), general.get_curr_timestamp_ms()
                if params != "" and len(params):
                    param_str = self.params_to_str(params,0)
                    payload_str = request_path + str(reqId) + self.key + param_str + str(nonce)
                    req = self.request_builder(params, payload_str, request_path, reqId, nonce)
                    url = self.domain_url + request_path
                    response = requests.post(url, data=req, headers=common_headers)
                    return response.json()
                else:
                    payload_str = request_path + str(reqId) + self.key + str(nonce)
                    url = self.domain_url + request_path
                    req = self.request_builder(params, payload_str, request_path, reqId, nonce)
                    response = requests.post(url, data=req, headers=common_headers)
                    return response.json()
            except Exception as e:
                raise e
    
    
    def _unsignedRequest(self, method, apiUrl, params):
        url = self.domain_url + apiUrl
        if method == 'GET':
            try:
                response = requests.request('get', url, params=params)
                return response.json()
            except Exception as e:
                raise e
        else:
            raise Exception(f"{method} Method not supported for unsigned calls")

    ## parsers
    def _parseBalance(self, balData):
        parsedBal = {"free": {}, "total": {}}
        if balData['code'] != 0: raise Exception(balData['message'])
        for bal in balData['result']['accounts']:
            parsedBal["free"][bal["currency"]] = float(bal["available"])
            parsedBal["total"][bal["currency"]] = float(bal['balance'])
        return parsedBal
    
    def _parseCreateOrder(self, order):
        if order['code'] != 0: raise Exception(order['message'])
        parsedOrder = {}
        parsedOrder["id"] = order['result']["order_id"]
        parsedOrder["symbol"] = None
        parsedOrder["price"] = None
        parsedOrder["amount"] = None
        parsedOrder["side"] = None
        parsedOrder["timestamp"] = None
        parsedOrder["status"] = None
        parsedOrder["orderJson"] = json.dumps(order)
        return parsedOrder
    
    def _parseCancelOrder(self, order):
        if order['code'] != 0: raise Exception(order['message'])
        parsedOrder = {}
        parsedOrder["id"] = None
        parsedOrder["symbol"] = None
        parsedOrder["price"] = None
        parsedOrder["amount"] = None
        parsedOrder["side"] = None
        parsedOrder["timestamp"] = None
        parsedOrder["status"] = None
        parsedOrder["orderJson"] = json.dumps(order)
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
        parsedOrder["id"] = order.get('order_id', None)
        parsedOrder["symbol"] = self._getUserSymbol(order["instrument_name"]) if "instrument_name" in order else None
        parsedOrder["price"] = float(order["price"]) if "price" in order else None 
        parsedOrder["amount"] = float(order["quantity"]) if "quantity" in order else None
        parsedOrder["side"] = order['side'].lower()
        parsedOrder["timestamp"] = int(order["create_time"]) if "create_time" in order else None
        parsedOrder["status"] = order.get("status", None)
        parsedOrder["orderJson"] = json.dumps(order) if order else None 
        return parsedOrder
    
    def _parseOpenOrders(self, orders):
        if orders['code'] != 0: raise Exception(orders['message'])
        parsedOrderList = []
        for order in orders['result']['order_list']:
            parsedOrderList.append(self._parseOrder(order))
        return parsedOrderList
    
    def _parseTrades(self, trades):
        def parseTrade(trade):
            parsedTrade = {}
            parsedTrade["id"] = trade.get("order_id", None)
            parsedTrade["tradeId"] = trade.get("trade_id", None)
            parsedTrade["side"] = trade["side"].lower()
            parsedTrade["price"] = trade.get("traded_price", None)
            parsedTrade["amount"] = trade.get("traded_quantity", None)
            parsedTrade["takerOrMaker"] = None # cc doesnt return taker or maker role
            if "create_time" in trade:
                parsedTrade["timestamp"] = int(float(trade["create_time"]))
                parsedTrade["datetime"] = general.ts_to_datetime(parsedTrade["timestamp"])
            else: 
                parsedTrade["timestamp"] = None
                parsedTrade["datetime"] = None
            parsedTrade["fee"] = trade.get("fee", None)
            parsedTrade["fee_currency"] = trade.get("fee_currency", None)
            return parsedTrade
        if trades['code'] != 0: raise Exception(trades['message'])
        parsedTradeList = []
        for trade in trades['result']['trade_list']:
            parsedTradeList.append(parseTrade(trade))
        return parsedTradeList

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
        body = {
            "instrument_name": self._getSymbol(symbol),
            "side": side.upper(),
            "type": "LIMIT",
            "price": price,
            "quantity": amount
        }
        body.update(params)
        apiUrl = "private/create-order"
        try:
            resp = self._signedRequest(method='POST', request_path=apiUrl, params=body)
            return self._parseCreateOrder(resp)
        except Exception as e:
            raise e

    def create_market_order(self, symbol, amount, side, params={}):
        if side == 'buy':
            body = {
                "instrument_name": self._getSymbol(symbol),
                "side": side.upper(),
                "type": "MARKET",
                "notional": amount
            }
        else:
            body = {
                "instrument_name": self._getSymbol(symbol),
                "side": side.upper(),
                "type": "MARKET",
                "quantity": amount
            }
        body.update(params)
        apiUrl = "private/create-order"
        try:
            resp = self._signedRequest(method='POST', request_path=apiUrl, params=body)
            return self._parseCreateOrder(resp)
        except Exception as e:
            raise e
    
    def fetch_order(self, id, symbol=None):
        raise NotImplementedError("method not implemented")

    def fetch_open_orders(self, symbol=None,  kwargs=None):
        apiUrl = "private/get-open-orders"
        params = {"instrument_name": self._getSymbol(symbol)}
        try:
            resp = self._signedRequest(method='POST', request_path=apiUrl, params=params)
            return self._parseOpenOrders(resp)
        except Exception as e:
            raise e
        
    def cancel_order(self, id, symbol=None):
        apiUrl = "private/cancel-order"
        params = {"instrument_name": self._getSymbol(symbol), "order_id": id}
        try:
            resp = self._signedRequest(method='POST', request_path=apiUrl, params=params)
            return self._parseCancelOrder(resp)
        except Exception as e:
            raise e

    def fetch_ticker(self, symbol: str, params={}) -> baseTypes.Ticker:
        raise NotImplementedError("method not implemented")
    
    def fetch_balance(self, params={}) -> baseTypes.Balances:
        apiUrl = "private/get-account-summary"
        try:
            resp = self._signedRequest(method='POST', request_path=apiUrl, params={})
            return self._parseBalance(resp)
        except Exception as e:
            raise e
        
    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        if symbol:
            params['instrument_name'] = self._getSymbol(symbol)
        if limit:
            params['page_size'] = limit
        if since:
            params['start_ts'] = int(since)
        apiUrl = "private/get-trades"
        try:
            resp = self._signedRequest(method='POST', request_path=apiUrl, params={})
            return self._parseTrades(resp)
        except Exception as e:
            raise e
        
    def fetch_order_book(self, symbol: str, limit=None, params={}) -> baseTypes.OrderBook:
        apiUrl = f"/spot/order_book"
        queryParams = {"currency_pair": self._getSymbol(symbol)}
        if limit is not None:
            queryParams["limit"] = int(limit)
        queryParams.update(params)
        try:
            resp = self._unsignedRequest('GET', apiUrl, params=queryParams)
            return self._parseOrderbook(resp)
        except Exception as e:
            raise e
    
    # parsed OHLCV = [[ts_ms, o, h ,l ,c, v],[]]
    def fetch_ohlcv(self, symbol: str, timeframe='1m', since = None, limit = None, params={}):
        raise NotImplementedError("method not implemented")