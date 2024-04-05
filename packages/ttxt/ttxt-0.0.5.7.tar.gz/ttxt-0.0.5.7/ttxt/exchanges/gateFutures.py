import hmac
import base64
import hashlib
import json
import time
import requests
from ttxt.base import baseFuturesExchange
from ttxt.types import baseTypes


class gateFutures(baseFuturesExchange.BaseFuturesExchange):
    def __init__(self, key, secret, **kwargs):
        super().__init__(key, secret, **kwargs)
        self.domain_url = "https://api.gateio.ws"  # host + prefix
        self.prefix = "/api/v4"
        self.settle_currency = "usdt"
        self.quanto_multiplier = {}

    def _getSymbol(self, symbol):
        return symbol.replace("/", "_")
    
    def _getUserSymbol(self, symbol):
        return symbol.replace("_", "/")

    def setQuantMultiplier(self, ticker):
        self.quanto_multiplier[ticker] = float(self.fetch_ticker(self._getSymbol(ticker))["quanto_multiplier"])

    ## Auth 
    def gen_sign(self, method, url, query_string=None, payload_string=None):
        key = self.key
        secret = self.secret
        t = time.time()
        m = hashlib.sha512()
        m.update((payload_string or "").encode('utf-8'))
        hashed_payload = m.hexdigest()
        s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
        sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
        return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}

    def connectToPrivateWss(self, creds, ticker):
        request = {
            "time": int(time.time()),
            "channel": "spot.orders",
            "event": "subscribe",  # "unsubscribe" for unsubscription
            "payload": [ticker]
        }
        # refer to Authentication section for gen_sign implementation
        request['auth'] = self.gen_sign(request['channel'], request['event'], request['time'], creds)
        return json.dumps(request) 

    ## Requests 
    def _signedRequest(self, request_path, method, queryString, body):
        common_headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        if method == "GET":
            try:
                if queryString != "" and len(queryString):
                    url = self.domain_url+ self.prefix + request_path + "?" + queryString
                else:
                    url = self.domain_url+ self.prefix + request_path
                sign_headers = self.gen_sign('GET', self.prefix + request_path, queryString, "")
                sign_headers.update(common_headers)
                response = requests.get(url, headers=sign_headers)
                return response.json()
            except Exception as e:
                raise e
        if method == "POST":
            try:
                if queryString and queryString != "" and len(queryString):
                    url = self.domain_url+ self.prefix + request_path + "?" + queryString
                    sign_headers = self.gen_sign('POST', self.prefix + request_path, queryString, "")
                    sign_headers.update(common_headers)
                    response = requests.post(url, headers=sign_headers)
                else:
                    url = self.domain_url+ self.prefix + request_path
                    request_content = json.dumps(body)
                    sign_headers = self.gen_sign('POST', self.prefix + request_path, "", request_content)
                    sign_headers.update(common_headers)
                    url = self.domain_url + self.prefix + request_path
                    response = requests.post(url, headers=sign_headers, data=request_content)
                return response.json()
            except Exception as e:
                raise e
        if method == "DELETE":
            try:
                url = self.domain_url+ self.prefix + request_path
                sign_headers = self.gen_sign('DELETE', self.prefix + request_path, queryString, "")
                sign_headers.update(common_headers)
                response = requests.delete(url, headers=sign_headers)
                return response.json()
            except Exception as e:
                raise e
    
    def _unsignedRequest(self, method, apiUrl, params):
        url = self.domain_url + self.prefix + apiUrl
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
        if 'message' in balData:
            raise Exception(balData['message'])
        parsedBal = {"free": {}, "total": {}, "unrealisedPnl": {}}
        parsedBal["free"][balData["currency"]] = balData.get("available", None)
        parsedBal["total"][balData["currency"]] = balData.get("total", None)
        parsedBal["unrealisedPnl"][balData["currency"]] = balData.get("unrealised_pnl", None)
        return parsedBal
    
    def _parseOrderbook(self, orderbookData):
        parsedData = {}
        parsedData["datetime"] = None
        parsedData["timestamp"] = orderbookData.get("current", None)
        parsedData["nonce"] = orderbookData.get("id", None)
        if "bids" in orderbookData:
            parsedData["bids"] = [[float(d['p']), float(d['s'])] for d in orderbookData["bids"]]
        else: parsedData["bids"] = []
        if "asks" in orderbookData:
            parsedData["asks"] = [[float(d['p']), float(d['s'])] for d in orderbookData["asks"]]
        else: parsedData["asks"] = []
        return parsedData
    
    '''
    {'stp_id': 0, 'id': 375076070136, 'biz_info': '-', 'mkfr': '0.00015', 'tkfr': '0.0004', 'tif': 'gtc', 
    'refu': 0, 'create_time': 1701883378.318, 'price': '43920.1', 'size': 10, 'status': 'open', 
    'iceberg': 0, 'is_liq': False, 'amend_text': '-', 'left': 10, 'text': 'api', 'fill_price': '0', 
    'user': 13632672, 'update_id': 1, 'refr': '0', 'is_reduce_only': False, 'stp_act': '-', 'is_close': False, 
    'contract': 'BTC_USDT'}
    '''
    def _parseOrder(self, order):
        parsedOrder = {}
        parsedOrder["id"] = order.get('id', None)
        parsedOrder["symbol"] = self._getUserSymbol(order["contract"]) if "contract" in order else None
        parsedOrder["price"] = float(order["price"]) if "price" in order else None 
        parsedOrder["amount"] = float(order["size"]) if "size" in order else None
        if parsedOrder["amount"]:
            parsedOrder["side"] = "buy" if parsedOrder["amount"] > 0 else "sell"
        else:
            parsedOrder["side"] = None
        parsedOrder["timestamp"] = float(order["create_time"]) if "create_time" in order else None
        parsedOrder["status"] = order["status"] if "status" in order else None
        parsedOrder["orderJson"] = json.dumps(order) if order else None 
        return parsedOrder
    
    def _parseCreateOrder(self, order):
        if 'message' in order:
            raise Exception(order['message'])
        parsedOrder = {}
        parsedOrder["id"] = order.get('id', None)
        parsedOrder["symbol"] = self._getUserSymbol(order["contract"]) if "contract" in order else None
        parsedOrder["price"] = float(order["price"]) if "price" in order else None 
        parsedOrder["amount"] = float(order["size"]) if "size" in order else None
        if parsedOrder["amount"]:
            parsedOrder["side"] = "buy" if parsedOrder["amount"] > 0 else "sell"
        else:
            parsedOrder["side"] = None
        parsedOrder["timestamp"] = float(order["create_time"]) if "create_time" in order else None
        parsedOrder["status"] = order["status"] if "status" in order else None
        parsedOrder["orderJson"] = json.dumps(order) if order else None 
        return parsedOrder
    
    def _parseOpenOrders(self, orders):
        if 'message' in orders:
            raise Exception(orders['message'])
        parsedOrderList = []
        for order in orders:
            parsedOrderList.append(self._parseOrder(order))
        return parsedOrderList
    
    def _parseCandlesticks(self, candletickData):
        parsedCandlesticks = []
        for kline in candletickData:
            parsedCandlesticks.append([int(kline["t"])*1000, float(kline["o"]), float(kline["h"]), float(kline["l"]), float(kline["c"]), float(kline["v"])])
        return parsedCandlesticks

    ## Exchange functions 

    # https://www.gate.io/docs/developers/apiv4/en/#create-a-futures-order
    def create_order(self, symbol, type, side, amount, price=None, params={}):
        try:
            ticker = self._getSymbol(symbol)
            if ticker not in self.quanto_multiplier:
                self.setQuantMultiplier(ticker=ticker)
            amount = float(amount) / self.quanto_multiplier[ticker]
            amount = -1*amount if (side == 'sell') else amount # negative amount for side==sell
            if type == "market":
                body = {
                    "contract": self._getSymbol(symbol),
                    "size": amount,
                    "iceberg": params["iceberg"] if "iceberg" in params else 0,
                    "close": params["close"] if "close" in params else False,
                    "reduce_only": params["reduce_only"] if "reduce_only" in params else False,
                    "tif": params["tif"] if "tif" in params else "gtc",
                    "text": params["text"] if "text" in params else "",
                    "auto_size": params["auto_size"] if "auto_size" in params else "", #Set side to close dual-mode position. close_long closes the long side; while close_short the short one. Note size also needs to be set to 0
                    "stp_act": params["stp_act"] if "stp_act" in params else "-"
                }
            elif type == "limit":
                body = {
                    "contract": self._getSymbol(symbol),
                    "size": amount,
                    "price": float(price),
                    "iceberg": params["iceberg"] if "iceberg" in params else 0,
                    "close": params["close"] if "close" in params else False,
                    "reduce_only": params["reduce_only"] if "reduce_only" in params else False,
                    "tif": params["tif"] if "tif" in params else "gtc",
                    "text": params["text"] if "text" in params else "",
                    "auto_size": params["auto_size"] if "auto_size" in params else "", #Set side to close dual-mode position. close_long closes the long side; while close_short the short one. Note size also needs to be set to 0
                    "stp_act": params["stp_act"] if "stp_act" in params else "-"
                }
            apiUrl = f"/futures/{self.settle_currency}/orders"
            response = self._signedRequest(method='POST', request_path=apiUrl, queryString="", body=body)
            return self._parseCreateOrder(response)
        except Exception as e:
            raise e
    
    def fetch_order(self, id, symbol=None):
        apiUrl = f"/futures/{self.settle_currency}/orders/{id}"
        try:
            resp = self._signedRequest(method='GET', request_path=apiUrl, queryString='', body=None)
            return self._parseOrder(resp)
        except Exception as e:
            raise e

    def fetch_open_orders(self, symbol=None,  kwargs=None):
        apiUrl = f"/futures/{self.settle_currency}/orders"
        try:
            query_param = 'status=open'
            resp = self._signedRequest(method='GET', request_path=apiUrl, queryString=query_param, body=None)
            return self._parseOpenOrders(resp)
        except Exception as e:
            raise e
        
    def cancel_order(self, id, symbol=None):
        apiUrl = f"/futures/{self.settle_currency}/orders/{id}"
        try:
            resp = self._signedRequest(method='DELETE', request_path=apiUrl, queryString='', body=None)
            return self._parseCreateOrder(resp)
        except Exception as e:
            raise e

    def fetch_ticker(self, symbol: str, params={}) -> baseTypes.Ticker:
        apiUrl = f"/futures/{self.settle_currency}/contracts/{self._getSymbol(symbol)}"
        try:
            resp = self._unsignedRequest('GET', apiUrl, params='')
            return resp # parse this response into Ticker
        except Exception as e:
            raise e
    
    def fetch_balance(self, params={}) -> baseTypes.Balances:
        apiUrl = '/futures/usdt/accounts'
        try:
            resp = self._signedRequest(method='GET', request_path=apiUrl, body=None, queryString=params)
            return self._parseBalance(resp)
        except Exception as e:
            raise e
        
    def set_leverage(self, leverage, symbol, params={}):
        apiUrl = f'/futures/usdt/positions/{self._getSymbol(symbol)}/leverage'
        try:
            query_param = f'leverage={leverage}'
            resp = self._signedRequest(method='POST', request_path=apiUrl, body=None, queryString=query_param)
            return resp
        except Exception as e:
            raise e
        
    def fetch_order_book(self, symbol: str, limit=None, params={}) -> baseTypes.OrderBook:
        apiUrl = f"/futures/{self.settle_currency}/order_book"
        queryParams = {"contract": self._getSymbol(symbol)}
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
        apiUrl = f"/futures/{self.settle_currency}/candlesticks"
        queryParams = {"contract": self._getSymbol(symbol), "from": since, "limit": limit, "interval": timeframe}
        if limit is not None:
            queryParams["limit"] = int(limit)
        queryParams.update(params)
        try:
            resp = self._unsignedRequest('GET', apiUrl, params=queryParams)
            return self._parseCandlesticks(resp)
        except Exception as e:
            raise e