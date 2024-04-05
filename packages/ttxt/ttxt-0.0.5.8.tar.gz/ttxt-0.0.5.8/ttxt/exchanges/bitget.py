from email import header
import hmac
import base64
import hashlib
import json
import time
from wsgiref import headers
import requests
from urllib.parse import urlencode
from ttxt.utils import general
from ttxt.base import baseSpotExchange
from ttxt.types import baseTypes


class bitget(baseSpotExchange.BaseSpotExchange):
    def __init__(self, key, secret, password, **kwargs):
        super().__init__(key, secret, **kwargs)
        self.domain_url = "https://api.bitget.com"
        self.password = password
        self.success_sode = '00000'
        
    def _getSymbol(self, symbol):
        return symbol.replace("/", "")
    
    def _getUserSymbol(self, symbol):
        raise NotImplementedError("method not implemented")
    
    ## Auth 
    def sign(self, message):
        mac = hmac.new(bytes(self.secret, encoding='utf-8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d)
    
    def pre_hash(self, timestamp, method, request_path, queryString, body=None):
        if not body:
            return str(timestamp) + str.upper(method) + request_path + queryString
        return str(timestamp) + str.upper(method) + request_path + body
    
    def parse_params_to_str(self, params):
        params = [(key, val) for key, val in params.items()]
        params.sort(key=lambda x:x[0])
        url = "?" + urlencode(params)
        if url == '?':
            return ''
        return url
    
    def generate_timestamp(self):
        return int(time.time() * 10**3)
    
    def _signedRequest(self, method, request_path, queryString, body):
        timeMs = self.generate_timestamp()
        if method == "POST":
            body = json.dumps(body)
            queryString = json.dumps(queryString) if queryString is not None else ''
            signature = self.sign(self.pre_hash(timeMs, method, request_path, queryString ,body))
            headers = {"ACCESS-KEY": self.key, "ACCESS-SIGN": signature, "ACCESS-PASSPHRASE": self.password, "ACCESS-TIMESTAMP": str(timeMs), "locale": "en-US", "Content-Type": "application/json"}
            url = self.domain_url+request_path
            try:
                response = requests.post(url, headers=headers, data=body)
                return response.json()
            except Exception as e:
                raise e
        if method == "GET":
            params = queryString
            body = ""
            request_path = request_path + self.parse_params_to_str(params)
            signature = self.sign(self.pre_hash(timeMs, "GET", request_path, str(body)))
            headers = {"ACCESS-KEY": self.key, "ACCESS-SIGN": signature, "ACCESS-PASSPHRASE": self.password, "ACCESS-TIMESTAMP": str(timeMs), "locale": "en-US", "Content-Type": "application/json"}
            url = self.domain_url+request_path
            try:
                response = requests.get(url, headers=headers)
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
        if balData['code'] != '00000': 
            raise Exception(balData['msg'])
        data = balData.get("data", None)
        if data is not None:
            for element in data:
                parsedBal["free"][element["coin"]] = element.get("available", None)
                parsedBal["total"][element["coin"]] = str(float(element['available'])+float(element['frozen']))
        return parsedBal
    
    def _parseCreateorder(self, order):
        if order['code'] != '00000': 
            raise Exception(order['msg'])
        parsedOrder = {'id': None, "symbol": None, "amount": None, "side": None, "timestamp": None, "status": None, "orderJson": None}
        if "data" in order and order["data"] != {}:
            parsedOrder['id'] = order['data']['orderId']
            parsedOrder["orderJson"] = json.dumps(order)
        return parsedOrder
    
    def _parseOpenOrders(self, orderjson):
        if orderjson['code'] != '00000': 
            raise Exception(orderjson['msg'])
        parsedOrderList = []    
        if "data" in orderjson and orderjson['data'] != {}:
            for order in orderjson["data"]:
                order['price'] = order['priceAvg']
                parsedOrderList.append(self._parseOrder(order))
        return parsedOrderList
    
    def _parseOrder(self, order):
        parsedOrder = {}
        parsedOrder["id"] = order.get('orderId', None)
        parsedOrder["symbol"] = order.get('symbol', None)
        parsedOrder["price"] = float(order["price"]) if "price" in order else None 
        parsedOrder["amount"] = float(order["size"]) if "size" in order else None
        parsedOrder["side"] = order['side'].lower() if "side" in order else None
        parsedOrder["timestamp"] = int(order["cTime"]) if "cTime" in order else None
        parsedOrder["status"] = order.get("status", None)
        parsedOrder["orderJson"] = json.dumps(order) if order else None 
        return parsedOrder
    
    def _parseFetchOrder(self, data):
        parsedOrder = {"id": None, "symbol": None, "price": None, "amount": None, "takerOrMaker": None, "datetime": None, "fee": None, "fee_currency": None,
                       "side": None, "timestamp": None, "status": None}
        if "data" in data and data["data"] != {}:
            order = data['data']
            if type(order) == list:
                order = order[0]
            parsedOrder["id"] = order["orderId"]
            parsedOrder["tradeId"] = order.get("tradeId", None)
            parsedOrder["symbol"] = order["symbol"]
            if "price" in order:
                parsedOrder["price"] = float(order["price"])
            else:
                parsedOrder["price"] = float(order["priceAvg"])
            parsedOrder['takerOrMaker'] = order.get('tradeScope', None)
            parsedOrder["amount"] = float(order["size"])
            parsedOrder["side"] = order["side"].lower()
            parsedOrder["timestamp"] = int(order["uTime"])
            parsedOrder["datetime"] = general.ts_to_datetime(parsedOrder["timestamp"])
            parsedOrder["status"] = order.get('status', None)
            parsedOrder['fee'] = order.get("feeDetail", None).get('totalFee', None) if order.get("feeDetail", None) is not None else None
            parsedOrder["fee_currency"] = order["feeDetail"].get('feeCoin', None)
        return parsedOrder
    
    def _parseFetchTrades(self, orderjson):
        if orderjson['code'] != '00000': 
            raise Exception(orderjson['msg'])
        parsedTradesList = []
        if "data" in orderjson and orderjson["data"] != []:
            for order in orderjson["data"]:
                parsedTradesList.append(self._parseFetchOrder({'data': order}))
        return parsedTradesList
    
    def _parseCancelorder(self, order):
        if order['code'] != '00000': 
            raise Exception(order['msg'])
        parsedOrder = {'id': None, "symbol": None, "amount": None, "side": None, "timestamp": None, "status": None, "orderJson": None}
        if "data" in order and order["data"] != {}:
            parsedOrder['id'] = order['data']['orderId']
        return parsedOrder
    
    ## Exchange functions 
    def fetch_ticker(self, symbol):
        raise NotImplementedError("method not implemented")
    
    def fetch_balance(self, params={}) -> baseTypes.Balances:
        apiUrl = "/api/v2/spot/account/assets"
        try:
            resp = self._signedRequest('GET', apiUrl, params, '')
            return self._parseBalance(resp)
        except Exception as e:
            raise e
        
    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}): 
        apiUrl = "/api/v2/spot/trade/fills"
        try:
            params = {
                "symbol": self._getSymbol(symbol)
            }
            if since:
                params["startTime"] = since
            if 'endTime' in params and params['endTime']:
                params['endTime'] = params['endTime']
            if limit:
                params['limit'] = limit
            response = self._signedRequest('GET', request_path=apiUrl, queryString=params, body='')
            return self._parseFetchTrades(response)
        except Exception as e:
            raise e
    
    def create_order(self, symbol, side, amount, order_type, price=None, params={}): 
        apiUrl = "/api/v2/spot/trade/place-order"
        params = {
            "symbol": self._getSymbol(symbol),
            "force": "GTC",
            "side": side.lower(),
            "size": str(amount)
        }
        try:
            if order_type == 'limit':
                params["orderType"] = "limit"
                params['price'] = str(price)
            elif order_type == 'market':
                params["orderType"] = "market"
            params.update(params) 
            response = self._signedRequest('POST', request_path=apiUrl, body=params, queryString='')
            return self._parseCreateorder(response)
        except Exception as e:
            raise e
    
    def create_market_order(self, symbol, side, amount, params={}):
        apiUrl = "/api/v2/spot/trade/place-order"
        params = {
            "symbol": self._getSymbol(symbol),
            "orderType": "market",
            "side": side.lower(),
            "size": str(amount)
        }
        try:
            params.update(params) 
            response = self._signedRequest('POST', request_path=apiUrl, body=params, queryString='')
            return self._parseCreateorder(response)
        except Exception as e:
            raise e
    
    def create_limit_order(self, symbol, side, amount, price, params={}):
        apiUrl = "/api/v2/spot/trade/place-order"
        params = {
            "symbol": self._getSymbol(symbol),
            "orderType": "limit",
            "force": "GTC",
            "side": side.lower(),
            "price": str(price),
            "size": str(amount)
        }
        try:
            params.update(params) 
            response = self._signedRequest('POST', request_path=apiUrl, body=params, queryString='')
            return self._parseCreateorder(response)
        except Exception as e:
            raise e
    
    def cancel_order(self, id=None, symbol=None, params={}):
        apiUrl = "/api/v2/spot/trade/cancel-order"
        ticker = self._getSymbol(symbol)
        try:
            params={}
            if id is not None:
                params['orderId'] = id
            if symbol is not None:
                params['symbol'] = str(ticker)
            params.update(params)
            response = self._signedRequest('POST', request_path=apiUrl, queryString='',body=params)
            return self._parseCancelorder(response)
        except Exception as e:
            raise e
    
    def fetch_open_orders(self, symbol=None, kwargs=None):
        apiUrl = "/api/v2/spot/trade/unfilled-orders"
        ticker = self._getSymbol(symbol)
        try:
            params = {
                'symbol': ticker,
                'endTime': self.generate_timestamp(),
                'limit': 100,
            }
            response = self._signedRequest('GET', request_path=apiUrl, queryString=params, body='')
            return self._parseOpenOrders(response)
        except Exception as e:
            raise e
    
    def fetch_order(self, id, symbol = None, params={}):
        apiUrl = "/api/v2/spot/trade/orderInfo"
        try:
            params = {
                'orderId': id
            }
            params.update(params)
            response = self._signedRequest('GET', request_path=apiUrl, queryString=params, body='')
            return self._parseFetchOrder(response)
        except Exception as e:
            raise e

    ## use case specifci request    
    def sub_account_transfer(self, amount, fromUserId, toUserId, coin, fromType="spot", toType="spot"):
        apiUrl = "/api/v2/spot/wallet/subaccount-transfer"
        params = {
            "fromType": fromType,
            "toType": toType,
            "amount": amount,
            "coin": coin,
            "fromUserId": fromUserId,
            "toUserId": toUserId
        }
        try:
            response = self._signedRequest('POST', request_path=apiUrl, body=params, queryString='')
            return response
        except Exception as e:
            raise e