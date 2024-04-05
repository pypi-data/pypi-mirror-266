import hmac
import base64
import hashlib
import json
import time
import requests
from ttxt.base import baseSpotExchange
from ttxt.types import baseTypes
from ttxt.utils import general


class gateio(baseSpotExchange.BaseSpotExchange):
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
                if queryString != "" and len(queryString):
                    url = self.domain_url+ self.prefix + request_path + "?" + queryString
                else:
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
    # gateio doesnt return 'total' for spot accounts so, total=available
    def _parseBalance(self, balData):
        if 'label' in balData: raise Exception(balData['message'])
        parsedBal = {"free": {}, "total": {}}
        for bal in balData:
            parsedBal["free"][bal["currency"]] = bal.get("available", None)
            parsedBal["total"][bal["currency"]] = bal.get("total", parsedBal["free"][bal["currency"]])
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
    
    '''
    {'id': '523236767452', 'text': 'apiv4', 'amend_text': '-', 'create_time': '1709553380', 
    'update_time': '1709553380', 'create_time_ms': 1709553380379, 'update_time_ms': 1709553380379,
      'status': 'open', 'currency_pair': 'GAL_USDT', 'type': 'limit', 'account': 'spot', 
      'side': 'buy', 'amount': '1', 'price': '3.3', 'time_in_force': 'gtc', 'iceberg': '0', 
      'left': '1', 'filled_amount': '0', 'fill_price': '0', 'filled_total': '0', 'fee': '0', 
      'fee_currency': 'GAL', 'point_fee': '0', 'gt_fee': '0', 'gt_maker_fee': '0', 
      'gt_taker_fee': '0', 'gt_discount': False, 'rebated_fee': '0', 
      'rebated_fee_currency': 'USDT', 'finish_as': 'open'}
    '''
    def _parseOrder(self, order):
        parsedOrder = {}
        parsedOrder["id"] = order.get('id', None)
        parsedOrder["symbol"] = self._getUserSymbol(order["currency_pair"]) if "currency_pair" in order else None
        parsedOrder["price"] = float(order["price"]) if "price" in order else None 
        parsedOrder["amount"] = float(order["amount"]) if "amount" in order else None
        parsedOrder["side"] = order.get('side', None)
        parsedOrder["timestamp"] = int(float(order["create_time"])) if "create_time" in order else None
        parsedOrder["status"] = order["status"] if "status" in order else None
        parsedOrder["orderJson"] = json.dumps(order) if order else None 
        return parsedOrder
    
    def _parseCreateOrder(self, order):
        if 'label' in order: raise Exception(order['message'])
        parsedOrder = {}
        parsedOrder["id"] = order.get('id', None)
        parsedOrder["symbol"] = self._getUserSymbol(order["currency_pair"]) if "currency_pair" in order else None
        parsedOrder["price"] = float(order["price"]) if "price" in order else None 
        parsedOrder["amount"] = float(order["amount"]) if "amount" in order else None
        parsedOrder["side"] = order.get('side', None)
        parsedOrder["timestamp"] = int(float(order["create_time"])) if "create_time" in order else None
        parsedOrder["status"] = order["status"] if "status" in order else None
        parsedOrder["orderJson"] = json.dumps(order) if order else None 
        return parsedOrder
    
    def _parseOpenOrders(self, orders):
        parsedOrderList = []
        if 'label' in orders: raise Exception(orders['message'])
        for order in orders:
            parsedOrderList.append(self._parseOrder(order))
        return parsedOrderList
    
    '''
    {'id': '7697129236', 'create_time': '1709562413', 'create_time_ms': '1709562413816.639000', 
    'currency_pair': 'GAL_USDT', 'side': 'buy', 'role': 'taker', 'amount': '0.29', 
    'price': '3.3558', 'order_id': '523332716519', 'fee': '0.0002465', 
    'fee_currency': 'GAL', 'point_fee': '0.0', 'gt_fee': '0.0', 'amend_text': '-', 
    'sequence_id': '380802', 'text': 'apiv4'}
    '''
    def _parseTrades(self, trades):
        def parseTrade(trade):
            parsedTrade = {}
            parsedTrade["id"] = trade.get("order_id", None)
            parsedTrade["tradeId"] = trade.get("id", None)
            parsedTrade["side"] = trade.get("side", None)
            parsedTrade["price"] = trade.get("price", None)
            parsedTrade["amount"] = trade.get("amount", None)
            parsedTrade["takerOrMaker"] = trade.get("role", None)
            if "create_time_ms" in trade:
                parsedTrade["timestamp"] = int(float(trade["create_time_ms"]))
                parsedTrade["datetime"] = general.ts_to_datetime(parsedTrade["timestamp"])
            else: 
                parsedTrade["timestamp"] = None
                parsedTrade["datetime"] = None
            return parsedTrade
        parsedTradeList = []
        if 'label' in trades: raise Exception(trades['message'])
        for trade in trades:
            parsedTradeList.append(parseTrade(trade))
        return parsedTradeList

    ## Exchange functions 

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        try:
            if type == "market":
                body = {
                    "currency_pair": self._getSymbol(symbol),
                    "type": "market",
                    "account": "spot",
                    "side": side,
                    "iceberg": params["iceberg"] if "iceberg" in params else "0",
                    "amount": str(amount),
                    "time_in_force": params["time_in_force"] if "time_in_force" in params else "ioc",
                }
            elif type == "limit":
                body = {
                    "currency_pair": self._getSymbol(symbol),
                    "type": "limit",
                    "account": "spot",
                    "side": side,
                    "iceberg": params["iceberg"] if "iceberg" in params else "0",
                    "amount": str(amount),
                    "price": str(price),
                    "time_in_force": params["time_in_force"] if "time_in_force" in params else "gtc",
                    "auto_borrow": params["auto_borrow"] if "auto_borrow" in params else False,
                }
            apiUrl = f"/spot/orders"
            response = self._signedRequest(method='POST', request_path=apiUrl, queryString="", body=body)
            return self._parseCreateOrder(response)
        except Exception as e:
            raise e
        
    def create_limit_order(self, symbol, amount, side, price, params={}):
        body = {
            "currency_pair": self._getSymbol(symbol),
            "type": "limit",
            "account": "spot",
            "side": side,
            "iceberg": params["iceberg"] if "iceberg" in params else "0",
            "amount": str(amount),
            "price": str(price),
            "time_in_force": params["time_in_force"] if "time_in_force" in params else "gtc",
            "auto_borrow": params["auto_borrow"] if "auto_borrow" in params else False,
        }
        apiUrl = f"/spot/orders"
        try:
            response = self._signedRequest(method='POST', request_path=apiUrl, queryString="", body=body)
            return self._parseCreateOrder(response)
        except Exception as e:
            raise e

    def create_market_order(self, symbol, amount, side, params={}):
        body = {
            "currency_pair": self._getSymbol(symbol),
            "type": "market",
            "account": "spot",
            "side": side,
            "iceberg": params["iceberg"] if "iceberg" in params else "0",
            "amount": str(amount),
            "time_in_force": params["time_in_force"] if "time_in_force" in params else "ioc",
        }
        apiUrl = f"/spot/orders"
        try:
            response = self._signedRequest(method='POST', request_path=apiUrl, queryString="", body=body)
            return self._parseCreateOrder(response)
        except Exception as e:
            raise e
    
    def fetch_order(self, id, symbol=None):
        raise NotImplementedError("method not implemented")

    def fetch_open_orders(self, symbol=None,  kwargs=None):
        apiUrl = "/spot/orders"
        try:
            query_param = f'currency_pair={self._getSymbol(symbol)}&status=open'
            resp = self._signedRequest(method='GET', request_path=apiUrl, queryString=query_param, body=None)
            return self._parseOpenOrders(resp)
        except Exception as e:
            raise e
        
    def cancel_order(self, id, symbol=None):
        apiUrl = f"/spot/orders/{id}"
        query_param = f'currency_pair={self._getSymbol(symbol)}'
        try:
            resp = self._signedRequest(method='DELETE', request_path=apiUrl, queryString=query_param, body=None)
            return self._parseCreateOrder(resp)
        except Exception as e:
            raise e

    def fetch_ticker(self, symbol: str, params={}) -> baseTypes.Ticker:
        raise NotImplementedError("method not implemented")
    
    def fetch_balance(self, params={}) -> baseTypes.Balances:
        apiUrl = '/spot/accounts'
        try:
            resp = self._signedRequest(method='GET', request_path=apiUrl, body=None, queryString=params)
            return self._parseBalance(resp)
        except Exception as e:
            raise e
        
    def fetch_my_trades(self, symbol, since=None, limit=None, params={}):
        apiUrl = '/spot/my_trades'
        query_params = ''
        if symbol:
            query_params += f'currency_pair={self._getSymbol(symbol)}'
        if limit:
            query_params += f'&limit={limit}'
        if since:
            query_params += f'&from={int(since)}'
        if 'to' in params and params['to']:
            query_params += f'&to={int(params["to"])}'
        if 'page' in params and params['page']:
            query_params += f'&page={int(params["page"])}'
        try:
            resp = self._signedRequest(method='GET', request_path=apiUrl, body=None, queryString=query_params)
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