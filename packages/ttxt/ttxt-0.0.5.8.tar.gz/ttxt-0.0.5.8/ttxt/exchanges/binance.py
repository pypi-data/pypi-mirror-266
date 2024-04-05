from ast import parse
from email import header
import hmac
import base64
import hashlib
import json
import time
from wsgiref import headers
import requests
from urllib.parse import urlencode
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from ttxt.base import baseSpotExchange
from ttxt.types import baseTypes
from ttxt.utils import general

class binance(baseSpotExchange.BaseSpotExchange):
    def __init__(self, key, secret, **kwargs):
        super().__init__(key, secret, **kwargs)
        self.domain_url = "https://api.binance.com"
        
    def _getSymbol(self, symbol):
        return symbol.replace("/", "")
    
    def generate_timestamp(self):
        """
        Return a millisecond integer timestamp.
        """
        return int(time.time() * 10**3)
    
    # Auth
    def sign(self, message):
        mac = hmac.new(self.secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
        return mac
    
    def parse_params_to_str(self, message):
        url = ''
        if message:
            url=urlencode(message)
        if url == '':
            return ''
        return url
    
    def _signedRequest(self, method, request_path, queryString, body):
        timeMs = self.generate_timestamp()
        if method == "POST":
            body["timestamp"] = timeMs
            bodyParse = self.parse_params_to_str(body)
            query = self.parse_params_to_str(queryString)
            body['signature'] = self.sign(queryString+bodyParse)
            body = query+self.parse_params_to_str(body)
            headers = {
                "X-MBX-APIKEY": self.key
            }
            if query == '':
                url = self.domain_url+request_path
            else:
                url = self.domain_url+request_path+'?'+query
            try:
                response = requests.request(method, url, headers=headers, data=body)
                return response.json()
            except Exception as e:
                raise e
        elif method == "GET"  or method == "DELETE":
            body = json.dumps(body)
            queryString["timestamp"] = timeMs
            queryString['signature'] = self.sign(self.parse_params_to_str(queryString))
            query = self.parse_params_to_str(queryString)
            headers = {
                "X-MBX-APIKEY": self.key
            }
            url = self.domain_url+request_path+'?'+query
            try:
                response = requests.request(method, url, headers=headers)
                return response.json()
            except Exception as e:
                raise e
            
    # Parsers
    def _parseBalance(self, balData):
        parsedBal = {"free": {}, "total": {}}
        if 'code' in balData:
            raise Exception(balData['msg'])
        data = balData.get("balances", None)
        for asset in data:
            if float(asset['free']) or float(asset['locked']):
                parsedBal["free"][asset["asset"]] = asset.get("free", None) 
                parsedBal["total"][asset["asset"]] = str(float(asset.get("free", None))+float(asset.get("locked", None)))
        return parsedBal
    
    def _parseCreateorder(self, order):
        parsedOrder = {'id': None, "symbol": None, "amount": None, "side": None, "timestamp": None, "status": None, "orderJson": None}
        if 'code' in order:
            raise Exception(order['msg'])
        parsedOrder['id'] = order.get("orderId", None)
        parsedOrder['symbol'] = order.get("symbol", None)
        parsedOrder['amount'] = order.get("executedQty", None)
        parsedOrder['side'] = order.get("side", None)
        parsedOrder['status'] = order.get("type", None)
        parsedOrder['timestamp'] = order.get("transactTime", None)
        parsedOrder["orderJson"] = json.dumps(order)
        return parsedOrder
    
    def _parseOpenOrders(self, orders):
        if 'code' in orders:
            raise Exception(orders['msg'])
        parsedOrderList = []
        for order in orders:
            parsedOrderList.append(self._parseOrder(order))
        return parsedOrderList
    
    def _parseOrder(self, order):
        parsedOrder = {}
        parsedOrder["id"] = order.get('orderId', None)
        parsedOrder["symbol"] = order.get('symbol', None)
        parsedOrder["price"] = float(order["price"]) if "price" in order else None 
        parsedOrder["amount"] = float(order["origQty"]) if "origQty" in order else None
        parsedOrder["side"] = order['side'].lower() if "side" in order else None
        parsedOrder["timestamp"] = order["updateTime"] if "updateTime" in order else None
        parsedOrder["status"] = order.get("status", None)
        parsedOrder["orderJson"] = json.dumps(order) if order else None 
        return parsedOrder
    
    def _parseCancelorder(self, order):
        parsedOrder = {'id': None, "symbol": None, "amount": None, "side": None, "timestamp": None, "status": None, "orderJson": None}
        if 'code' in order:
            raise Exception(order['msg'])
        parsedOrder['id'] = order.get("orderId", None)
        parsedOrder['symbol'] = order.get("symbol", None)
        parsedOrder['amount'] = order.get("origQty", None)
        parsedOrder['side'] = order.get("side", None)
        parsedOrder['status'] = order.get("status", None)
        if order.get("transactTime"):
            parsedOrder['timestamp'] = int(order.get("transactTime"))
        else:
            parsedOrder['timestamp'] = None
        return parsedOrder
    
    def _parseFetchTrades(self, orderData):
        parsedTradesList = []
        if 'code' in orderData:
            raise Exception(orderData['msg'])
        for order in orderData:
            parsedTradesList.append(self._parseTrades(order))
        return parsedTradesList
    
    def _parseTrades(self, order):
        parsedOrder = {"id": None, "symbol": None, "price": None, "amount": None, "takerOrMaker": None, "datetime": None, "fee": None, "fee_currency": None,
                       "side": None, "timestamp": None, "status": None}
        parsedOrder['id'] = order.get("orderId", None)
        parsedOrder["tradeId"] = order.get("id", None)
        parsedOrder['symbol'] = order.get("symbol", None)
        parsedOrder['amount'] = order.get("qty", None)
        parsedOrder['price'] = order.get("price", None)
        parsedOrder["side"] = "buy" if order["isBuyer"] else "sell"
        if order["isMaker"]:
            parsedOrder['takerOrMaker'] = 'maker'
        else:
            parsedOrder['takerOrMaker'] = 'taker'
        if order.get("time"):
            parsedOrder['timestamp'] = int(order.get("time"))
        else:
            parsedOrder['timestamp'] = None
        parsedOrder['datetime'] = general.ts_to_datetime(parsedOrder["timestamp"]) if parsedOrder['timestamp'] else None
        parsedOrder["status"] = order.get('status', None)
        parsedOrder["fee_currency"] = order.get('commissionAsset', None)
        parsedOrder['fee'] = order.get("commission", None)
        return parsedOrder
    
    # Exchange functions 
    def fetch_balance(self, params={}) -> baseTypes.Balances:
        apiUrl = "/api/v3/account"
        try:
            params = {
            }
            response = self._signedRequest('GET', apiUrl, queryString=params, body='')
            return self._parseBalance(response)
        except Exception as e:
            raise e
    
    def create_order(self, symbol, side, amount, order_type, price=None, params={}):
        apiUrl = "/api/v3/order"
        try:
            params = {
                "symbol": self._getSymbol(symbol),
                "side": side.upper(),
                "type": order_type.upper(),
                "quantity": amount
            }
            if order_type == "limit":
                params["price"] = price
                params["timeInForce"] = "GTC"
            response = self._signedRequest('POST', request_path=apiUrl, body=params, queryString='')
            return self._parseCreateorder(response)
        except Exception as e:
            raise e
    
    def create_market_order(self, symbol, side, amount, params={}):
        return self.create_order(symbol, side, amount=amount, price=None, order_type='market', params={})
    
    def create_limit_order(self, symbol, side, amount, price, params={}):
        return self.create_order(symbol, side, amount, order_type='limit', price=price, params={})
    
    def cancel_order(self, id, symbol=None, params={}):
        apiUrl = "/api/v3/order"
        try:
            params = {
                "orderId": id
            }
            if symbol:
                params["symbol"] = self._getSymbol(symbol)
            response = self._signedRequest('DELETE', request_path=apiUrl, queryString=params, body='')
            return self._parseCancelorder(response)
        except Exception as e:
            raise e
    
    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}): 
        apiUrl = "/api/v3/myTrades"
        try:
            params = {
                "symbol": self._getSymbol(symbol),
            }
            if since:
                params["startTime"] = since
            if 'endTime' in params and params['endTime']:
                params['endAt'] = params['endTime']
            if limit:
                params['limit'] = limit
            response = self._signedRequest('GET', request_path=apiUrl, queryString=params, body='')
            return self._parseFetchTrades(response)
        except Exception as e:
            raise e
    
    def fetch_open_orders(self, symbol=None, kwargs=None):
        apiUrl = "/api/v3/openOrders"
        try:
            params = {
                "symbol": self._getSymbol(symbol)
            }
            response = self._signedRequest("GET", request_path=apiUrl, queryString=params, body='')
            return self._parseOpenOrders(response)
        except Exception as e:
            raise e