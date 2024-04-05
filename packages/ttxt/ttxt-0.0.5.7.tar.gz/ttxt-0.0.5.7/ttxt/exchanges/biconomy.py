import hmac
import base64
import hashlib
import json
import time
import requests
from datetime import datetime as dt
from ttxt.base import baseSpotExchange
from ttxt.types import baseTypes

'''
kwards = {}
'''
class biconomy(baseSpotExchange.BaseSpotExchange):
    def __init__(self, key, secret, **kwargs):
        super().__init__(key, secret, **kwargs)
        self.domain_url = "https://www.biconomy.com"
        self.max_retries = 5
        self.symbolLotSize = {}

    def _getSymbol(self, symbol):
        return symbol.replace("/", "_")
    
    def _getUserSymbol(self, symbol):
        return symbol.replace("_", "/")
    
    ## Auth 
    def get_expire(self):
        return int((time.time() + 1) * 1000)  # websockets use seconds
    
    def generate_timestamp(self):
        """
        Return a millisecond integer timestamp.
        """
        return int(time.time() * 10**3)
    
    def _get_sign(self, payload):
        # payload = ":"+ payload + "&secret_key=" + self.secret
        payload = payload + "&secret_key=" + self.secret
        signature = hashlib.md5(payload.encode()).hexdigest().upper()
        return signature
        
    def _parseParams(self, paramsMap):
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        # return paramsStr+"&timestamp="+str(int(time.time() * 1000))
        return paramsStr
    
    def _check_resp_status(self, resp):
        if "code" in resp:
            if resp["code"] != 0:
                raise Exception(resp["message"])
            else:
                return resp  # success 
        if "message" in resp:
            raise Exception(resp["message"])
        raise Exception("Unknown error")

    def _send_request(self, method, path, params, payload={}):
        # self._send_request(method='POST', path=apiUrl, params=params, payload={})
        # url = "%s%s?%s&sign=%s" % (self.domain_url, path, params, self._get_sign(params))
        paramsForReq = params.copy()
        params.update({"api_key": self.key})
        params = self._parseParams(params)
        sign = self._get_sign(params)
        # params = params + "&sign=" + sign
        url = "%s%s" % (self.domain_url, path)
        headers = {
            'X-SITE-ID': "127",
            "Content-type": "application/x-www-form-urlencoded"
        }
        try:
            updatedurl = url + "?api_key=" + self.key + "&sign=" + sign
            response = requests.post(updatedurl, headers=headers, data=paramsForReq)
            return self._check_resp_status(response.json())
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
            # req_params = self._prepare_params(query)
            req_params = self._prepare_params(query)
            # Authenticate if we are using a private endpoint.
            headers = {'X-SITE-ID': "127"}
            if method == "GET":
                try:
                    if req_params:
                        client = requests.Session()
                        r = client.prepare_request(requests.Request(method, path, headers=headers))
                        r = requests.get(path + f"?{req_params}", headers=headers)
                    else:
                        r = requests.get(path, headers=headers)
                    return r.json()
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
        parsedBal= {"free": {}, "total": {}}
        if "result" in balData and balData["result"]:
            for key, val in balData["result"].items():
                if key != "user_id":
                    parsedBal["free"][key] = float(val["available"])
                    parsedBal["total"][key] = float(val["available"]) + float(val["freeze"])
        return parsedBal
    
    '''
    {'code': 0, 'message': 'Successful operation', 'result': {'amount': '0.001', 'ctime': 1703112715.647542, 
    'deal_fee': '0', 'deal_money': '0', 'deal_stock': '0', 'id': 45576367001, 'left': '0.001', 'maker_fee': '0',
    'market': 'BTC_USDT', 'mtime': 1703112715.647542, 'price': '41900', 'side': 2, 'source': 'api,127', 'taker_fee': '0', 
    'type': 1, 'user': 51340387}}
    '''
    def _parseCreateorder(self, order, openOrders=False):
        parsedOrder = {}
        if openOrders:
            parsedOrder["id"] = order.get('id', None)
            parsedOrder["symbol"] = order.get('market', None)
            parsedOrder["price"] = float(order["price"])
            parsedOrder["amount"] = float(order["amount"])
            side = order.get('side', None)
            if not side:
                parsedOrder["side"] = None
            else:
                parsedOrder["side"] = "buy" if side == 2 else "sell" 
            parsedOrder["timestamp"] = int(order["ctime"])*1000
            parsedOrder["status"] = "open"
            parsedOrder["orderJson"] = json.dumps(order)
        else:
            if "result" in order and order["result"]:
                parsedOrder["id"] = order["result"].get('id', None)
                parsedOrder["symbol"] = order["result"].get('market', None)
                parsedOrder["price"] = float(order["result"]["price"])
                parsedOrder["amount"] = float(order["result"]["amount"])
                side = order["result"].get('side', None)
                if not side:
                    parsedOrder["side"] = None
                else:
                    parsedOrder["side"] = "buy" if side == 2 else "sell" 
                parsedOrder["timestamp"] = int(order["result"]["ctime"])*1000
                parsedOrder["status"] = "open"
                parsedOrder["orderJson"] = json.dumps(order["result"])
        return parsedOrder

    def _parseOpenOrders(self, orders):
        parsedOrderList = []
        if "result" in orders and "records" in orders["result"]:
            for order in orders["result"]["records"]:
                parsedOrderList.append(self._parseCreateorder(order, openOrders=True))
        return parsedOrderList

    def _parseTickerInfo(self, data, ticker):
        for tickerInfo in data:
            if tickerInfo["symbol"] == self._getSymbol(ticker):
                return tickerInfo
        return {}

    ## Exchange functions 

    def create_market_sell_order(self, symbol, amount, params={}, price=None):
        apiUrl = "/api/v1/private/trade/market"
        try:
            ticker = self._getSymbol(symbol)
            params = {
                'market': self._getSymbol(ticker),
                'side': 1,
                'amount': str(amount)
            }
            params.update(params) 
            response = self._send_request(method='POST', path=apiUrl, params=params)
            return self._parseCreateorder(response)
        except Exception as e:
            raise e
        
    def create_market_buy_order(self, symbol, amount, params={}, price=None):
        apiUrl = "/api/v1/private/trade/market"
        try:
            ticker = self._getSymbol(symbol)
            params = {
                'market': self._getSymbol(ticker),
                'side': 2,
                'amount': amount
            }
            params.update(params) 
            response = self._send_request(method='POST', path=apiUrl, params=params)
            return self._parseCreateorder(response)
        except Exception as e:
            raise e

    def create_limit_order(self, symbol, side, price, amount, params={}):
        ticker = self._getSymbol(symbol)
        if symbol not in self.symbolLotSize:
            resp = self.fetch_ticker(ticker)
            self.symbolLotSize[symbol] = resp
        # handle precisions 
        price = round(price, self.symbolLotSize[symbol]['quoteAssetPrecision'])
        amount = round(amount, self.symbolLotSize[symbol]['baseAssetPrecision'])
        
        apiUrl = "/api/v1/private/trade/limit"
        try:
            params = {
                'market': ticker,
                'side': 1 if side == "sell" else 2,
                'amount': str(amount),
                'price': str(price)
            }
            params.update(params) 
            response = self._send_request(method='POST', path=apiUrl, params=params)
            return self._parseCreateorder(response)
        except Exception as e:
            raise e
    
    def fetch_order(self, id, symbol=None):
        apiUrl = "/api/v1/private/order/pending/detail"
        try:
            ticker = self._getSymbol(symbol)
            params = {
                'market': ticker,
                'order_id': id
            }
            response = self._send_request(method='POST', path=apiUrl, params=params)
            return self._parseCreateorder(response)
        except Exception as e:
            raise e

    '''
    {"code":0,"message":"Successful operation","result":{"limit":100,"offset":0,
    "records":[{"amount":"0.001","ctime":1703070656.073618,"deal_fee":"0","deal_money":"0",
    "deal_stock":"0","id":45529401586,"left":"0.001","maker_fee":"0","market":"BTC_USDT",
    "mtime":1703070656.073618,"price":"41900","side":2,"source":"api,127","taker_fee":"0",
    "type":1,"user":51340387},{"amount":"0.001","ctime":1703012664.528346,"deal_fee":"0",
    "deal_money":"0","deal_stock":"0","id":45466363178,"left":"0.001","maker_fee":"0",
    "market":"BTC_USDT","mtime":1703012664.528346,"price":"41900","side":2,"source":"api,127",
    "taker_fee":"0","type":1,"user":51340387},{"amount":"0.001","ctime":1703011778.993588,
    "deal_fee":"0","deal_money":"0","deal_stock":"0","id":45465387414,"left":"0.001","maker_fee":"0"
    ,"market":"BTC_USDT","mtime":1703011778.993588,"price":"41900","side":2,"source":"api,127",
    "taker_fee":"0","type":1,"user":51340387}],"total":3}}
    '''
    def fetch_open_orders(self, symbol=None,  kwargs=None):
        apiUrl = "/api/v1/private/order/pending"
        try:
            ticker = self._getSymbol(symbol)
            params = {
                # 'api_key': self.key,
                'market': self._getSymbol(ticker),
                'offset': 0,
                'limit': 100
            }
            response = self._send_request(method='POST', path=apiUrl, params=params)
            return self._parseOpenOrders(response)
        except Exception as e:
            raise e
    
    '''
    {"code":0,"message":"Successful operation","result":{"amount":"0.001","ctime":1703071266.005806,
    "deal_fee":"0","deal_money":"0","deal_stock":"0","id":45530059627,"left":"0.001","maker_fee":"0",
    "market":"BTC_USDT","mtime":1703071266.005806,"price":"41900","side":2,"source":"api,127",
    "taker_fee":"0","type":1,"user":51340387}}
    '''
    def cancel_order(self, id, symbol=None, params={}):
        apiUrl = "/api/v1/private/trade/cancel"
        ticker = self._getSymbol(symbol)
        try:
            params = {
                'market': self._getSymbol(ticker),
                'order_id': id
            }
            response = self._send_request(method='POST', path=apiUrl, params=params)
            return self._parseCreateorder(response)
        except Exception as e:
            raise e

    def fetch_ticker(self, symbol: str, params={}) -> baseTypes.Ticker:
        apiUrl = "/api/v1/exchangeInfo"
        try:
            resp = self._unsignedRequest(method='GET', path=apiUrl)
            return self._parseTickerInfo(resp, symbol) # parse this response into Ticker
        except Exception as e:
            raise e
    
    # params = {"startTime": 1702512246000, "endTime": 1702512248000, "limit": 100}
    def fetch_ohlcv(self, symbol, interval, size, params={}):
       raise NotImplementedError
        
    def fetch_balance(self, params={}) -> baseTypes.Balances:
        apiUrl = '/api/v1/private/user'
        try:
            resp = self._send_request(method='POST', path=apiUrl, params={}, payload=None)
            return self._parseBalance(resp)
        except Exception as e:
            raise e