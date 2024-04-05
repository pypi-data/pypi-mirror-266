import hmac
import base64
import hashlib
import json
import datetime
import requests
from urllib import parse
import urllib.parse
from datetime import datetime as dt
from ttxt.base import baseSpotExchange
from ttxt.types import baseTypes
from ttxt.utils import general
# Requests will use simplejson if available.
try:
    from simplejson.errors import JSONDecodeError
except ImportError:
    from json.decoder import JSONDecodeError

class RestApiRequest(object):

    def __init__(self):
        self.method = ""
        self.url = ""
        self.host = ""
        self.post_body = ""
        self.header = dict()
        self.json_parser = None

class UrlParamsBuilder(object):

    def __init__(self):
        self.param_map = dict()
        self.post_map = dict()
        self.post_list = list()

    def put_url(self, name, value):
        if value is not None:
            if isinstance(value, (list, dict)):
                self.param_map[name] = value
            else:
                self.param_map[name] = str(value)

    def put_post(self, name, value):
        if value is not None:
            if isinstance(value, (list, dict)):
                self.post_map[name] = value
            else:
                self.post_map[name] = str(value)

    def build_url(self):
        if len(self.param_map) == 0:
            return ""
        encoded_param = urllib.parse.urlencode(self.param_map)
        return "?" + encoded_param

    def build_url_to_json(self):
        return json.dumps(self.param_map)

class huobi(baseSpotExchange.BaseSpotExchange):
    def __init__(self, key, secret, **kwargs):
        super().__init__(key, secret, **kwargs)
        self.domain_url = "https://api.huobi.pro"
        self.domain_url_2 = "https://api-aws.huobi.pro"
        self.prefix = "/api/v4"
        self.category = kwargs["category"] if "category" in kwargs else "spot"
        self.recv_window = kwargs["recv_window"] if "recv_window" in kwargs else "5000"
        self.account_type = kwargs["account_type"] if "account_type" in kwargs else "UNIFIED"
        self.max_retries = 5
        self.session = requests.Session()

    def _getSymbol(self, symbol):
        return "".join([x.lower() for x in symbol.split("/")])
    
    def _getUserSymbol(self, symbol):
        raise NotImplementedError("method not implemented") 
    
    def utc_now(self):
        return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    ## Auth 
    def create_signature(self, method, url, builder):
        if self.key is None or self.secret is None or self.key == "" or self.secret == "":
            raise Exception("API key and secret key are required")

        timestamp = self.utc_now()
        builder.put_url("AccessKeyId", self.key)
        builder.put_url("SignatureVersion", "2")
        builder.put_url("SignatureMethod", "HmacSHA256")
        builder.put_url("Timestamp", timestamp)

        host = urllib.parse.urlparse(url).hostname
        path = urllib.parse.urlparse(url).path

        keys = sorted(builder.param_map.keys())
        qs0 = '&'.join(['%s=%s' % (key, parse.quote(builder.param_map[key], safe='')) for key in keys])
        payload0 = '%s\n%s\n%s\n%s' % (method, host, path, qs0)
        dig = hmac.new(self.secret.encode('utf-8'), msg=payload0.encode('utf-8'), digestmod=hashlib.sha256).digest()
        s = base64.b64encode(dig).decode()
        builder.put_url("Signature", s)

    def __create_request_by_get_with_signature(self, url, builder):
        request = RestApiRequest()
        request.method = "GET"
        request.host = self.domain_url
        self.create_signature(request.method, request.host + url, builder)
        request.header.update({"Content-Type": "application/x-www-form-urlencoded"})
        request.url = url + builder.build_url()
        return request
    
    def __create_request_by_post_with_signature(self, url, builder):
        request = RestApiRequest()
        request.method = "POST"
        request.host = self.domain_url
        self.create_signature(request.method, request.host + url, builder)
        request.header.update({'Content-Type': 'application/json'})
        if (len(builder.post_list)):  # specify for case : /v1/order/batch-orders
            request.post_body = builder.post_list
        else:
            request.post_body = builder.post_map
        request.url = url + builder.build_url()
        return request
    
    def create_request(self, method, url, params):
        builder = UrlParamsBuilder()
        if params and len(params):
            if method == "GET" or method == "GET-UNSIGNED":
                for key, value in params.items():
                    builder.put_url(key, value)
            elif method == "POST" or method == "POST-UNSIGNED":
                for key, value in params.items():
                    builder.put_post(key, value)
            else:
                raise Exception("[error] undefined HTTP method")

        if method =="GET-UNSIGNED":
            request = self.__create_request_by_get(url, builder)
        elif method == "GET":
            request = self.__create_request_by_get_with_signature(url, builder)
        elif method == "POST":
            request = self.__create_request_by_post_with_signature(url, builder)
        else:
            raise Exception(method + "  is invalid http method")

        return request
    
    def _signedRequest(self, method, url, params, is_checked=False):
        request = self.create_request(method, url, params)
        if request.method == "GET":
            response = self.session.get(request.host + request.url, headers=request.header)
            if is_checked is True:
                return response.text
            dict_data = json.loads(response.text)
            return dict_data

        elif request.method == "POST":
            response = self.session.post(request.host + request.url, data=json.dumps(request.post_body), headers=request.header)
            dict_data = json.loads(response.text)
            return dict_data
    
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
        parsedBal = {"free": {}, "total": {}}
        if balData["status"] != "ok": raise Exception(balData["err-msg"])
        for balDataEle in balData["data"]["list"]:
            if balDataEle["type"] == "trade":
                parsedBal["free"][balDataEle["currency"].upper()] = float(balDataEle["balance"])
            if balDataEle["type"] == "frozen":
                parsedBal["total"][balDataEle["currency"].upper()] = float(balDataEle["balance"]) + parsedBal["free"][balDataEle["currency"].upper()]
        return parsedBal
    
    def _parseOrderbook(self, orderbookData):
        parsedData = {}
        parsedData["datetime"] = None
        parsedData["timestamp"] = orderbookData.get("ts", None)
        parsedData["nonce"] = orderbookData.get("u", None)
        if "b" in orderbookData:
            parsedData["bids"] = [[float(d[0]), float(d[1])] for d in orderbookData["b"]]
        else: parsedData["bids"] = []
        if "a" in orderbookData:
            parsedData["asks"] = [[float(d[0]), float(d[1])] for d in orderbookData["a"]]
        else: parsedData["asks"] = []
        return parsedData
    
    def _parseCreateOrder(self, order):
        parsedOrder = {}
        if order["status"] != "ok": raise Exception(order["err-msg"])
        parsedOrder["id"] = order["data"]
        parsedOrder["symbol"] = None
        parsedOrder["price"] = None
        parsedOrder["amount"] = None
        parsedOrder["side"] = None
        parsedOrder["timestamp"] = None
        parsedOrder["status"] = None
        parsedOrder["orderJson"] = json.dumps(order)
        return parsedOrder
    
    '''
    {'retCode': 0, 'retMsg': 'OK', 'result': {'orderId': 'f3708d4e-24d6-4528-9037-764d03610479', 'orderLinkId': ''}, 
    'retExtInfo': {}, 'time': 1702055115208}
    '''
    def _parseOrder(self, order):
        parsedOrder = {}
        parsedOrder["id"] = order["orderId"]
        parsedOrder["symbol"] = order.get('symbol', None)
        parsedOrder["price"] = order.get('price', None)
        parsedOrder["amount"] = order.get('amount', None)
        parsedOrder["side"] = "buy" if order["type"].startswith("buy") else "sell"
        parsedOrder["timestamp"] = int(order["created-at"])
        parsedOrder["status"] = order.get('state', None)
        parsedOrder["orderJson"] = json.dumps(order)
        return parsedOrder

    def _parseOpenOrders(self, orders):
        parsedOrderList = []
        if order["status"] != "ok": raise Exception(order["err-msg"])
        for order in orders['data']:
            parsedOrderList.append(self._parseOrder(order))
        return parsedOrderList

    def _parseTrades(self, trades):
        def parseTrade(trade):
            parsedTrade = {}
            parsedTrade["id"] = trade.get("order-id", None)
            parsedTrade["tradeId"] = trade.get("trade-id", None)
            parsedTrade["symbol"] = trade.get("symbol", None)
            parsedTrade["side"] = "buy" if trade["type"].startswith("buy") else "sell"
            parsedTrade["price"] = trade.get("price", None)
            parsedTrade["amount"] = trade.get("filled-amount", None)
            parsedTrade["takerOrMaker"] = trade["role"]
            if "created-at" in trade:
                parsedTrade["timestamp"] = trade["created-at"]
                parsedTrade["datetime"] = general.ts_to_datetime(parsedTrade["timestamp"])
            else: 
                parsedTrade["timestamp"] = None
                parsedTrade["datetime"] = None
            parsedTrade["feeCurrency"] = trade["fee-currency"]
            parsedTrade["fee"] = trade["filled-fees"]
            return parsedTrade
        parsedTradeList = []
        if trades["status"] != "ok": raise Exception(trades["err-msg"])
        for trade in trades["data"]:
            parsedTradeList.append(parseTrade(trade))
        return parsedTradeList


    ## Exchange functions 

    # https://www.gate.io/docs/developers/apiv4/en/#create-a-futures-order
    def create_order(self, symbol, type, side, amount, price=None, params={}):
        try:
            if type == "limit":
                return self.create_limit_order(symbol, amount, side, price, params={})
            elif type == "market":
                return self.create_market_order(symbol, amount, side, params={})
        except Exception as e:
            raise e
    
    def create_limit_order(self, symbol, amount, side, price, params={}):
        body = {
            "account-id": self.fetch_accounts(),
            "amount": amount,
            "price": price,
            "source": "spot-api",
            "symbol": self._getSymbol(symbol),
            "type": "buy-limit" if side == "buy" else "sell-limit"
        }
        apiUrl = "/v1/order/orders/place"
        try:
            resp = self._signedRequest(method='POST', url=apiUrl, params=body)
            return self._parseCreateOrder(resp)
        except Exception as e:
            raise e
        
    def create_market_order(self, symbol, amount, side, params={}):
        body = {
            "account-id": self.fetch_accounts(),
            "amount": amount,
            "source": "spot-api",
            "symbol": self._getSymbol(symbol),
            "type": "buy-market" if side == "buy" else "sell-market"
        }
        apiUrl = "/v1/order/orders/place"
        try:
            resp = self._signedRequest(method='POST', url=apiUrl, params=body)
            return self._parseCreateOrder(resp)
        except Exception as e:
            raise e
    
    def fetch_order(self, id, symbol=None):
        raise NotImplementedError("method not implemented")

    def fetch_open_orders(self, symbol=None,  kwargs=None):
        apiUrl = "/v1/order/openOrders"
        params = {"symbol": self._getSymbol(symbol)}
        try:
            resp = self._signedRequest(method='GET', url=apiUrl, params=params)
            return self._parseOpenOrders(resp)
        except Exception as e:
            raise e
        
    def cancel_order(self, id, symbol=None, params={}):
        apiUrl = f"/v1/order/orders/{id}/submitcancel"
        body = {
            "order_id" : id
        }
        try:
            resp = self._signedRequest(method='POST', url=apiUrl, params=body)
            return self._parseCreateOrder(resp)
        except Exception as e:
            raise e

    def fetch_ticker(self, symbol: str, params={}) -> baseTypes.Ticker:
        raise NotImplementedError("method not implemented")
    
    def fetch_accounts(self):
        apiUrl = '/v1/account/accounts'
        try:
            resp = self._signedRequest(method='GET', url=apiUrl, params={})
            if resp['status'] != "ok": raise Exception("error fetching accounts")
            return resp['data'][0]['id']
        except Exception as e:
            raise e
    
    def fetch_balance(self, params={}) -> baseTypes.Balances:
        accountId = self.fetch_accounts()
        apiUrl = f"/v1/account/accounts/{accountId}/balance"
        try:
            resp = self._signedRequest(method='GET', url=apiUrl, params={})
            return self._parseBalance(resp)
        except Exception as e:
            raise e
    
    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        apiUrl = '/v1/order/matchresults'
        queryParams = {"symbol": self._getSymbol(symbol)}
        if since:
            queryParams["start-time"] = since
        if limit:
            queryParams["size"] = limit
        if 'endTime' in params:
            queryParams["end-time"] = params['endTime']
        try:
            resp = self._signedRequest(method='GET', url=apiUrl, params=queryParams)
            return self._parseTrades(resp)
        except Exception as e:
            raise e
        
    def fetch_order_book(self, symbol: str, limit=None, params={}) -> baseTypes.OrderBook:
        raise NotImplementedError("method not implemented")
        
    def fetch_ohlcv(self, symbol: str, timeframe='1m', since = None, limit = None, params={}):
        raise NotImplementedError("Subclasses must implement this method")