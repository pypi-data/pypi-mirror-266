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
kwargs = {}
'''
class mexc(baseSpotExchange.BaseSpotExchange):
    def __init__(self, key, secret, **kwargs):
        super().__init__(key, secret, **kwargs)
        self.domain_url = "https://api.mexc.com"
        self.max_retries = 5
        self.symbolLotSize = {}
        self.recvWindow = 60000

    def _getSymbol(self, symbol):
        return symbol.replace("/", "")

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
                raise Exception(resp["msg"])
            else:
                return resp  # success 
        if "message" in resp:
            raise Exception(resp["message"])
        return resp
    
    def _authenticate(self,params):
        params = self._prepare_params(params)
        signature = hmac.new(
            self.secret.encode('utf-8'), 
            params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest() 
        headers = {
            'X-MEXC-APIKEY': self.key
        }
        updatedParams = params + f"&signature={signature}"
        return headers, updatedParams
        
    def _send_request(self, method, path, params, payload={}):
        headers, updatedParams = self._authenticate(params)
        try:
            updatedurl = self.domain_url + path + "?"+ updatedParams
            headers.update({'Content-Type': 'application/json'})
            if method == "GET":
                response = requests.get(updatedurl, headers=headers)
                return self._check_resp_status(response.json())
            if method == "POST":
                response = requests.post(updatedurl, headers=headers)
                return self._check_resp_status(response.json())
            if method == "DELETE":
                response = requests.delete(updatedurl, headers=headers)
                return self._check_resp_status(response.json())
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
        
    def _prepare_params(self, params):
        payload = "&".join(
                [
                    str(k) + "=" + str(v)
                    for k, v in params.items()  #use for sort: sorted(params.items())
                    if v is not None
                ]
            )
        return payload

    ## parsers
    def _parseCreateorder(self, order):
        parsedOrder = {}
        parsedOrder["id"] = order.get('orderId', None)
        parsedOrder["symbol"] = order.get('symbol', None)
        parsedOrder["price"] = order.get("price", None)
        parsedOrder["amount"] = order.get("origQty", None)
        if "side" in order: 
            parsedOrder["side"] = order["side"].lower()
        else:
            parsedOrder["side"] = None
        parsedOrder["timestamp"] = order.get("transactTime", None)
        parsedOrder["status"] = "closed"
        parsedOrder["orderJson"] = json.dumps(order)
        return parsedOrder

    '''
    {'makerCommission': None, 'takerCommission': None, 'buyerCommission': None, 
    'sellerCommission': None, 'canTrade': True, 'canWithdraw': True, 'canDeposit': True, 
    'updateTime': None, 'accountType': 'SPOT', 'balances': [{'asset': 'USDT', 
    'free': '59727.7100003983', 'locked': '0'}, {'asset': 'USDC', 'free': '2216', 
    'locked': '0'}, {'asset': 'GAL', 'free': '89.65', 'locked': '0'}, {'asset': 
    'OPUL', 'free': '790.15', 'locked': '0'}], 'permissions': ['SPOT']}
    '''
    def _parseBalance(self, balanceData):
        parsedBal = {"free": {}, "total": {}}
        if "balances" not in balanceData:
            return parsedBal
        for bal in balanceData["balances"]:
            parsedBal["free"][bal["asset"]] = bal.get("free", None)
            if "free" in bal and "locked" in bal:
                parsedBal["total"][bal["asset"]] = float(bal["free"]) + float(bal["locked"])
            else: parsedBal["free"][bal["asset"]] = bal.get("free", None)
        return parsedBal

    def _parseOpenOrders(self, orders):
        parsedOrderList = []
        for order in orders:
            parsedOrderList.append(self._parseCreateorder(order))
        return parsedOrderList
    
    def _parseOrderbook(self, orderbookData):
        parsedData = {}
        parsedData["datetime"] = None
        parsedData["timestamp"] = orderbookData.get("timestamp", None)
        parsedData["nonce"] = orderbookData.get("id", None)
        if "bids" in orderbookData:
            parsedData["bids"] = [[float(d[0]), float(d[1])] for d in orderbookData["bids"]]
        else: parsedData["bids"] = []
        if "asks" in orderbookData:
            parsedData["asks"] = [[float(d[0]), float(d[1])] for d in orderbookData["asks"]]
        else: parsedData["asks"] = []
        return parsedData

    def _parseTrades(self, trades):
        def parseTrade(trade):
            parsedTrade = {}
            parsedTrade["symbol"] = trade.get("symbol", None)
            parsedTrade["id"] = trade.get("orderId", None)
            parsedTrade["tradeId"] = trade.get("id", None)
            parsedTrade["side"] = "buy" if trade["isBuyer"] else "sell"
            parsedTrade["price"] = trade.get("price", None)
            parsedTrade["amount"] = trade.get("qty", None)
            parsedTrade["takerOrMaker"] = "maker" if trade["isMaker"] else "taker"
            if "time" in trade:
                parsedTrade["timestamp"] = int(float(trade["time"]))
                parsedTrade["datetime"] = general.ts_to_datetime(parsedTrade["timestamp"])
            else: 
                parsedTrade["timestamp"] = None
                parsedTrade["datetime"] = None
            parsedTrade["feeCurrency"] = trade["commissionAsset"]
            parsedTrade["fee"] = float(trade["commission"])
            return parsedTrade
        parsedTradeList = []
        for trade in trades:
            parsedTradeList.append(parseTrade(trade))
        return parsedTradeList

    ## Exchange functions
    # buy orders size are in quote and sell orders are in base
    def create_market_order(self, symbol, side, amount, params={}, price=None):
        apiUrl = "/api/v3/order"
        try:
            ticker = self._getSymbol(symbol)
            params = {
                'symbol': self._getSymbol(ticker),
                'side': side.upper(),
                'type': 'MARKET',
                'quantity': float(amount),
                'quoteOrderQty': float(amount),
                'recvWindow': self.recvWindow,
                'timestamp': self.generate_timestamp()
            }
            params.update(params) 
            response = self._send_request(method='POST', path=apiUrl, params=params)
            return self._parseCreateorder(response)
        except Exception as e:
            raise e
    
    def create_limit_order(self, symbol, side, amount, price, params={}):
        apiUrl = "/api/v3/order"
        try:
            ticker = self._getSymbol(symbol)
            params = {
                'symbol': self._getSymbol(ticker),
                'side': side.upper(),
                'type': 'LIMIT',
                'quantity': float(amount),
                'price': float(price),
                'quoteOrderQty': float(amount),
                'recvWindow': self.recvWindow,
                'timestamp': self.generate_timestamp()
            }
            params.update(params) 
            response = self._send_request(method='POST', path=apiUrl, params=params)
            return self._parseCreateorder(response)
        except Exception as e:
            raise e
    
    def fetch_order(self, id, symbol=None):
        raise NotImplementedError("method not implemented")
    
    def fetch_open_orders(self, symbol=None,  kwargs=None):
        apiUrl = '/api/v3/openOrders'
        params = {
            'symbol': self._getSymbol(symbol),
            'recvWindow': self.recvWindow,
            'timestamp': self.generate_timestamp()
        }
        try:
            resp = self._send_request(method='GET', path=apiUrl, params=params)
            return self._parseOpenOrders(resp)
        except Exception as e:
            raise e
        
    def cancel_order(self, id, symbol=None):
        apiUrl = '/api/v3/order'
        params = {
            'symbol': self._getSymbol(symbol),
            'orderId': id,
            'recvWindow': self.recvWindow,
            'timestamp': self.generate_timestamp()
        }
        try:
            resp = self._send_request(method='DELETE', path=apiUrl, params=params)
            return self._parseCreateorder(resp)
        except Exception as e:
            raise e
        
    def fetch_balance(self, params={}) -> baseTypes.Balances:
        apiUrl = '/api/v3/account'
        params = {
            'recvWindow': self.recvWindow,
            'timestamp': self.generate_timestamp()
        }
        try:
            resp = self._send_request(method='GET', path=apiUrl, params=params)
            return self._parseBalance(resp)
        except Exception as e:
            raise e
    
    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        apiUrl = '/api/v3/myTrades'
        params = {
            'timestamp': self.generate_timestamp(),
            'recvWindow': self.recvWindow
        }
        if symbol:
            params['symbol'] = self._getSymbol(symbol)
        if limit:
            params['limit'] = limit
        if since:
            params['startTime'] = int(since)
        if "endTime" in params:
            params['endTime'] = int(params["endTime"])
        try:
            resp = self._send_request(method='GET', path=apiUrl, params=params)
            return self._parseTrades(resp)
        except Exception as e:
            raise e
    
    def fetch_ticker(self, symbol: str, params={}) -> baseTypes.Ticker:
        raise NotImplementedError("method not implemented")

    def fetch_order_book(self, symbol: str, limit=None, params={}) -> baseTypes.OrderBook:
        apiUrl = f"/api/v3/depth"
        queryParams = {"symbol": self._getSymbol(symbol)}
        if limit is not None:
            queryParams["limit"] = int(limit)
        queryParams.update(params)
        try:
            resp = self._unsignedRequest('GET', apiUrl, params=queryParams)
            return self._parseOrderbook(resp)
        except Exception as e:
            raise e