from email import header
import hmac
import base64
import hashlib
import uuid
import json
from re import A
import time
from wsgiref import headers
import requests
from urllib.parse import urlencode
from ttxt.utils import general
from ttxt.base import baseSpotExchange
from ttxt.types import baseTypes

class kucoin(baseSpotExchange.BaseSpotExchange):
    def __init__(self, key, secret, password, **kwargs):
        super().__init__(key, secret, **kwargs)
        self.domain_url = "https://api.kucoin.com"
        self.passphrase = password
        
    def _getSymbol(self, symbol):
        return symbol.replace("/", "-")
    
    def _getUserSymbol(self, symbol):
        return symbol.replace("-", "/")
    
    def parse_params_to_str(self, params):
        paramsStr = "&".join(["%s=%s" % (key, val) for key, val in params.items()])
        url = "?" + paramsStr
        if url == '?':
            return ''
        return url
    
    # Auth
    def sign(self, message):
        mac = hmac.new(self.secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
        d = base64.b64encode(mac.digest())
        return d
    
    def pre_hash(self, timestamp, method, request_path, queryString, body=None):
        if not body:
            return str(timestamp) + str.upper(method) + request_path + self.parse_params_to_str(queryString)
        return str(timestamp) + str.upper(method) + request_path + body
    
    def generate_timestamp(self):
        return int(time.time() * 10**3)
    
    def _signedRequest(self, method, request_path, queryString=None, body=None):
        timeMS = self.generate_timestamp()
        if method == 'POST':
            data_json = json.dumps(body)
            queryString = json.dumps(queryString) if queryString is not None else ''
            signature = self.sign(self.pre_hash(timeMS, method, request_path, queryString='', body=data_json))
            passphrase = self.sign(self.passphrase)
            headers = {
                "KC-API-SIGN": signature,
                "KC-API-TIMESTAMP": str(timeMS),
                "KC-API-KEY": self.key,
                "KC-API-PASSPHRASE": passphrase,
                "KC-API-KEY-VERSION": "2",
                "Content-Type": "application/json" # specifying content type or using json=data in request
            }
            url = self.domain_url+request_path
            try:
                response = requests.request('POST', url, headers=headers, data=data_json)
                return response.json()
            except Exception as e:
                raise e
        if method == 'GET' or method == "DELETE":
            if queryString is None:
                queryString = ''
            signature = self.sign(self.pre_hash(timeMS, method, request_path, queryString, body=None))
            passphrase = self.sign(self.passphrase)
            headers = {
                "KC-API-SIGN": signature,
                "KC-API-TIMESTAMP": str(timeMS),
                "KC-API-KEY": self.key,
                "KC-API-PASSPHRASE": passphrase,
                "KC-API-KEY-VERSION": "2",
            }
            url = self.domain_url+request_path+self.parse_params_to_str(queryString)
            try:
                response = requests.request(method, url, headers=headers)
                return response.json()
            except Exception as e:
                raise e
        
    def _unsignedRequest(self, method, apiUrl, params):
        url = self.domain_url + apiUrl
        if method == 'GET':
            try:
                response = requests.request('GET', url, params=params)
                return response.json()
            except Exception as e:
                raise e
        else:
            raise Exception(f"{method} Method not supported for unsigned calls")
    
    ## parsers
    def _parseBalance(self, balData):
        if balData['code'] != '200000': 
            raise Exception(balData['msg'])
        parsedBal = {"free": {}, "total": {}}
        data = balData.get("data", None)
        if data is not None:
            for element in data:
                parsedBal["free"][element["currency"]] = element.get("available", None)
                parsedBal["total"][element["currency"]] = element.get("balance", None)
        return parsedBal
    
    def _parseCreateorder(self, orderData):
        if orderData['code'] != '200000': 
            raise Exception(orderData['msg'])
        parsedOrder = {'id': None, "symbol": None, "amount": None, "side": None, "timestamp": None, "status": None, "orderJson": None}
        if "data" in orderData and orderData["data"] != {}:
            parsedOrder['id'] = orderData['data']['orderId']
            parsedOrder["orderJson"] = json.dumps(orderData)
        return parsedOrder
    
    def _parseCancelorder(self, orderData):
        if orderData['code'] != '200000': 
            raise Exception(orderData['msg'])
        parsedOrder = {'id': None, "symbol": None, "amount": None, "side": None, "timestamp": None, "status": None, "orderJson": None}
        if "data" in orderData and "cancelledOrderIds" in orderData["data"] and type(orderData['data']['cancelledOrderIds']) == list:
            if not orderData['data']['cancelledOrderIds']:
                return parsedOrder
            else:
                parsedOrder['id'] = orderData['data']['cancelledOrderIds'][0]
        return parsedOrder
    
    def _parseOpenOrders(self, orderjson):
        parsedOrderList = []
        if "data" in orderjson and "items" in orderjson["data"]:
            for order in orderjson["data"]["items"]:
                parsedOrderList.append(self._parseOrder(order))
        return parsedOrderList
    
    def _parseOrder(self, order):
        parsedOrder = {}
        parsedOrder["id"] = order.get('id', None)
        parsedOrder["symbol"] = self._getUserSymbol(order.get('symbol', None))
        parsedOrder["price"] = float(order["price"]) if "price" in order else None 
        parsedOrder["amount"] = float(order["size"]) if "size" in order else None
        parsedOrder["side"] = order['side'].lower() if "side" in order else None
        parsedOrder["timestamp"] = order["createdAt"] if "cTime" in order else None
        parsedOrder["status"] = order.get("status", None)
        parsedOrder["orderJson"] = json.dumps(order) if order else None 
        return parsedOrder
    
    def _parseFetchTrades(self, orderData):
        if orderData['code'] != '200000': 
            raise Exception(orderData['msg'])
        parsedTradesList = []
        if "data" in orderData and "items" in orderData["data"]:
            for order in orderData["data"]['items']:
                parsedTradesList.append(self._parseTrades({'data': order}))
        return parsedTradesList
        
    def _parseTrades(self, data):
        parsedOrder = {"id": None, "symbol": None, "price": None, "amount": None, "takerOrMaker": None, "datetime": None, "fee": None, "fee_currency": None,
                       "side": None, "timestamp": None, "status": None}
        if "data" in data and data["data"] != {}:
            order = data['data']
            if type(order) == list:
                order = order[0]
            parsedOrder["id"] = order.get("orderId", None)
            parsedOrder["tradeId"] = order.get("tradeId", None)
            parsedOrder["symbol"] = self._getUserSymbol(order.get("symbol", None))
            if "price" in order:
                parsedOrder["price"] = float(order.get("price", None))
            else:
                parsedOrder["price"] = float(order.get("priceAvg", None))
            parsedOrder['takerOrMaker'] = order.get('liquidity', None)
            parsedOrder["amount"] = float(order.get("size", None))
            parsedOrder["side"] = order.get("side").lower()
            parsedOrder["timestamp"] = int(order["createdAt"])
            parsedOrder["datetime"] = general.ts_to_datetime(parsedOrder["timestamp"])
            parsedOrder["status"] = order.get('status', None)
            parsedOrder["fee_currency"] = order.get('feeCurrency', None)
            parsedOrder['fee'] = order.get("fee", None)
        return parsedOrder
    
    ## Exchange functions 
    def fetch_balance(self, params={}) -> baseTypes.Balances:
        apiUrl = "/api/v1/accounts"
        try:
            params = { "type": "trade" }
            response = self._signedRequest('GET', request_path=apiUrl, queryString=params)
            return self._parseBalance(response)
        except Exception as e:
            raise e
    
    def fetch_my_trades(self, symbol, since=None, limit=None, params={}): 
        apiUrl = "/api/v1/fills"
        try:
            params = {
                "symbol": self._getSymbol(symbol),
                "startAt": '0',
                "endAt": str(self.generate_timestamp())
            }
            if since is not None:
                params['startAt'] = since
            if 'endTime' in params and params['endTime']:
                params['endAt'] = params['endTime']
            response = self._signedRequest('GET', request_path=apiUrl, queryString=params, body='')
            return self._parseFetchTrades(response)
        except Exception as e:
            raise e
    
    def create_order(self, symbol, side, amount, order_type, price=None, params={}): # change body
        apiUrl = "/api/v1/orders"
        try:
            params = {
                "clientOid": str(uuid.uuid4()),
                "side": side,
                "symbol": self._getSymbol(symbol),
                "size": amount
            }
            if order_type == 'limit':
                params['type'] = 'limit'
                params['timeInForce'] = 'GTC'
                params["price"] = price
            if order_type == 'market':
                params['type'] = 'market'
            response = self._signedRequest('POST', request_path=apiUrl, body=params, queryString='')
            return self._parseCreateorder(response)
        except Exception as e:
            raise e
    
    def create_limit_order(self, symbol, side, amount, price, order_type=None, params={}):
        return self.create_order(symbol, side, amount=amount, price=price, order_type='limit', params={})
    
    def create_market_order(self, symbol, side, amount, order_type=None, price=None, params={}):
        return self.create_order(symbol, side, amount, order_type='market', price=None, params={})
    
    def cancel_order(self, id, symbol=None, params={}):
        apiUrl = "/api/v1/orders"
        try:
            params = {
                'orderId': id
            }
            response = self._signedRequest("DELETE", request_path=apiUrl, queryString=params)
            return self._parseCancelorder(response)
        except Exception as e:
            raise e
    
    def fetch_open_orders(self, symbol=None, kwargs=None):
        apiUrl = '/api/v1/orders'
        ticker = self._getSymbol(symbol)
        try:
            params = {
                'status': "active"
            }
            if symbol is not None:
                params['symbol'] = ticker
            response = self._signedRequest("GET", request_path=apiUrl, queryString=params, body='')
            return self._parseOpenOrders(response)
        except Exception as e:
            raise e