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
# Requests will use simplejson if available.
try:
    from simplejson.errors import JSONDecodeError
except ImportError:
    from json.decoder import JSONDecodeError

class WrongAccountType(Exception):
    """
    Exception raised for failed requests.

    Attributes:
        request -- The original request that caused the error.
        message -- Explanation of the error.
        status_code -- The code number returned.
        time -- The time of the error.
        resp_headers -- The response headers from API. None, if the request caused an error locally.
    """

    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code

class FailedRequestError(Exception):
    """
    Exception raised for failed requests.

    Attributes:
        request -- The original request that caused the error.
        message -- Explanation of the error.
        status_code -- The code number returned.
        time -- The time of the error.
        resp_headers -- The response headers from API. None, if the request caused an error locally.
    """

    def __init__(self, request, message, status_code, time, resp_headers):
        self.request = request
        self.message = message
        self.status_code = status_code
        self.time = time
        self.resp_headers = resp_headers
        super().__init__(
            f"{message.capitalize()} (ErrCode: {status_code}) (ErrTime: {time})"
            f".\nRequest → {request}."
        )

'''
kwards = {
    "category": "",
    "recv_window": ""
}
'''
class bybit(baseSpotExchange.BaseSpotExchange):
    def __init__(self, key, secret, **kwargs):
        super().__init__(key, secret, **kwargs)
        self.domain_url_testnet = "https://api-testnet.bybit.com"
        self.domain_url = "https://api.bybit.com"
        self.domain_url_2 = "https://api.bytick.com"
        self.category = kwargs["category"] if "category" in kwargs else "spot"
        self.recv_window = kwargs["recv_window"] if "recv_window" in kwargs else "5000"
        self.account_type = kwargs["account_type"] if "account_type" in kwargs else "UNIFIED"
        self.max_retries = 5
        self.symbolLotSize = {}

    def _getSymbol(self, symbol):
        return symbol.replace("/", "")
    
    def _getUserSymbol(self, symbol):
        return symbol.replace("_", "/") # TODO: change this 
    
    def _checkAndSetMinQty(self, ticker):
        if ticker in self.symbolLotSize and self.symbolLotSize[ticker] != {}:
            return 
        info = self.getInstrumentInfo(symbol=ticker)
        self.symbolLotSize = info["result"]["list"][0]["lotSizeFilter"]

    ## Auth 
    def get_expire(self):
        return int((time.time() + 1) * 1000)  # websockets use seconds
    
    def generate_timestamp(self):
        """
        Return a millisecond integer timestamp.
        """
        return int(time.time() * 10**3)

    def generate_signature(self, param_str):
        hash = hmac.new(
            bytes(self.secret, "utf-8"),
            param_str.encode("utf-8"),
            hashlib.sha256,
        )
        return hash.hexdigest()

    def prepare_payload(self, method, parameters):
        """
        Prepares the request payload and validates parameter value types.
        """

        def cast_values():
            string_params = [
                "qty",
                "price",
                "triggerPrice",
                "takeProfit",
                "stopLoss",
            ]
            integer_params = ["positionIdx"]
            for key, value in parameters.items():
                if key in string_params:
                    if type(value) != str:
                        parameters[key] = str(value)
                elif key in integer_params:
                    if type(value) != int:
                        parameters[key] = int(value)

        if method == "GET":
            payload = "&".join(
                [
                    str(k) + "=" + str(v)
                    for k, v in sorted(parameters.items())
                    if v is not None
                ]
            )
            return payload
        else:
            cast_values()
            return json.dumps(parameters)

    def _auth(self, payload, recv_window, timestamp):
        """
        Prepares authentication signature per Bybit API specifications.
        """

        if self.key is None or self.secret is None:
            raise PermissionError("Authenticated endpoints require keys.")
        param_str = str(timestamp) + self.key + str(recv_window) + payload
        return self.generate_signature(param_str)

    @staticmethod
    def _verify_string(self,params, key):
        if key in params:
            if not isinstance(params[key], str):
                return False
            else:
                return True
        return True
    
    def _checKRequest(self, s):
        if s.status_code != 200:
            if s.status_code == 403:
                error_msg = "You have breached the IP rate limit or your IP is from the USA."
            elif s.status_code == 401:
                error_msg = "Invalid request. Wrong access key or authentication in header"
            else:
                error_msg = "HTTP status code is not 200."
                raise WrongAccountType(message="Wrong account type", status_code=s.status_code)
            raise FailedRequestError(
                request=f"",
                message=error_msg,
                status_code=s.status_code,
                time=dt.utcnow().strftime("%H:%M:%S"),
                resp_headers=s.headers,
            )

            # Convert response to dictionary, or raise if requests error.
        try:
            return s.json()

        # If we have trouble converting, handle the error and retry.
        except JSONDecodeError as e:
            raise FailedRequestError(
                request=f"",
                message="Conflict. Could not decode JSON.",
                status_code=409,
                time=dt.utcnow().strftime("%H:%M:%S"),
                resp_headers=s.headers,
            )

    def _signedRequest(self, method=None, path=None, query=None, auth=False):
        """
        Submits the request to the API.

        Notes
        -------------------
        We use the params argument for the GET method, and data argument for
        the POST method. Dicts passed to the data argument must be
        JSONified prior to submitting request.

        """
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
            retries_remaining = f"{retries_attempted} retries remain."
            req_params = self.prepare_payload(method, query)
            # Authenticate if we are using a private endpoint.
            if auth:
                # Prepare signature.
                timestamp = self.generate_timestamp()
                signature = self._auth(
                    payload=req_params,
                    recv_window=recv_window,
                    timestamp=timestamp,
                )
                headers = {
                    "Content-Type": "application/json",
                    "X-BAPI-API-KEY": self.key,
                    "X-BAPI-SIGN": signature,
                    "X-BAPI-SIGN-TYPE": "2",
                    "X-BAPI-TIMESTAMP": str(timestamp),
                    "X-BAPI-RECV-WINDOW": str(recv_window),
                }
            else:
                headers = {}
            if method == "GET":
                try:
                    if req_params:
                        client = requests.Session()
                        r = client.prepare_request(requests.Request(method, path, headers=headers))
                        resp = requests.get(path + f"?{req_params}", headers=headers)
                    else:
                        resp = requests.get(path, headers=headers)
                    return self._checKRequest(resp)
                except Exception as e:
                    raise e
            if method == "POST":
                resp = requests.post( path, data=req_params, headers=headers)
                return self._checKRequest(resp)
            if method == "DELETE":
                resp = requests.delete( path, data=req_params, headers=headers)
                return self._checKRequest(resp)
    
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
    # balData = {"free": {"USDT": 1010, "BTC": ""}, "total": {"USDT": 1010, "BTC": 0}, "unrealisedPnl": {"USDT": 1010, "BTC": 0}}
    def _parseBalance(self, balData):
        if balData["retCode"]: raise Exception(balData["retMsg"])
        parsedBal = {"free": {}, "total": {}}
        balDataResult = balData.get("result", None)
        totalbalProp = "walletBalance"
        if 'balance' in balDataResult:
            balDatList = balDataResult["balance"]
            if len(balDatList) == 0:
                return parsedBal
        else:
            balDatList = balDataResult.get("list", [])
            if len(balDatList) == 0:
                return parsedBal
            balDatList = balDatList[0].get("coin", [])
            totalbalProp = "equity"
        if len(balDatList) == 0:
            return parsedBal
        for balDataEle in balDatList:
            parsedBal["free"][balDataEle["coin"]] = float(balDataEle["walletBalance"])
            parsedBal["total"][balDataEle["coin"]] = float(balDataEle[totalbalProp])
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
        if order['retCode'] != 0: raise Exception(order['retMsg'])
        parsedOrder["id"] = order['result']["orderId"]
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
        parsedOrder["side"] = order['side'].lower()
        parsedOrder["timestamp"] = int(order["createdTime"])
        parsedOrder["status"] = order.get('orderStatus', None)
        parsedOrder["orderJson"] = json.dumps(order)
        return parsedOrder

    def _parseOpenOrders(self, orders):
        parsedOrderList = []
        if orders['retCode'] != 0: raise Exception(orders['retMsg'])
        for order in orders['result']['list']:
            parsedOrderList.append(self._parseOrder(order))
        return parsedOrderList

    def _parseTrades(self, trades):
        def parseTrade(trade):
            parsedTrade = {}
            parsedTrade["id"] = trade.get("orderId", None)
            parsedTrade["tradeId"] = trade.get("execId", None)
            parsedTrade["symbol"] = trade.get("symbol", None)
            parsedTrade["side"] = trade["side"].lower()
            parsedTrade["price"] = trade.get("execPrice", None)
            parsedTrade["amount"] = trade.get("execQty", None)
            parsedTrade["takerOrMaker"] = "maker" if trade["isMaker"] else "taker"
            if "execTime" in trade:
                parsedTrade["timestamp"] = int(float(trade["execTime"]))
                parsedTrade["datetime"] = general.ts_to_datetime(parsedTrade["timestamp"])
            else: 
                parsedTrade["timestamp"] = None
                parsedTrade["datetime"] = None
            parsedTrade["feeCurrency"] = trade["feeCurrency"]
            parsedTrade["fee"] = trade["feeRate"]
            return parsedTrade
        parsedTradeList = []
        if trades['retCode'] != 0: raise Exception(trades['retMsg'])
        for trade in trades['result']['list']:
            parsedTradeList.append(parseTrade(trade))
        return parsedTradeList


    ## Exchange functions 

    # https://www.gate.io/docs/developers/apiv4/en/#create-a-futures-order
    def create_order(self, symbol, type, side, amount, price=None, params={}):
        try:
            ticker = self._getSymbol(symbol)
            self._checkAndSetMinQty(ticker=ticker)
            # TODO: check multiple for qty
            body = {
                "category": self.category,
                "symbol": ticker,
                "isLeverage": params["isLeverage"] if "isLeverage" in params else 1,  # 1 is for margin, 0 for spot
                "side": side.capitalize(),
                "orderType": type,
                "qty": float(amount),
                "timeInForce": params["timeInForce"] if "timeInForce" in params else "GTC",
                "positionIdx": params["positionIdx"] if "positionIdx" in params else 0,
            }
            body.update(params) 
            if type == "limit":
               body["price"] = float(price)
            apiUrl = "/v5/order/create"
            response = self._signedRequest(method='POST', path=apiUrl, query=body, auth=True)
            return self._parseCreateOrder(response)
        except Exception as e:
            raise e
    
    def create_limit_order(self, symbol, amount, side, price, params={}):
        ticker = self._getSymbol(symbol)
        body = {
            "category": self.category,
            "symbol": ticker,
            "isLeverage": params["isLeverage"] if "isLeverage" in params else 0,  # 1 is for margin, 0 for spot
            "side": side.capitalize(),
            "orderType": "Limit",
            "qty": float(amount),
            "price": float(price),
            "timeInForce": params["timeInForce"] if "timeInForce" in params else "GTC",
            "positionIdx": params["positionIdx"] if "positionIdx" in params else 0,
        }
        apiUrl = "/v5/order/create"
        try:
            response = self._signedRequest(method='POST', path=apiUrl, query=body, auth=True)
            return self._parseCreateOrder(response)
        except Exception as e:
            raise e
        
    def create_market_order(self, symbol, amount, side, params={}):
        ticker = self._getSymbol(symbol)
        body = {
            "category": self.category,
            "symbol": ticker,
            "isLeverage": params["isLeverage"] if "isLeverage" in params else 0,  # 1 is for margin, 0 for spot
            "side": side.capitalize(),
            "orderType": "Market",
            "qty": float(amount),
            "timeInForce": params["timeInForce"] if "timeInForce" in params else "GTC",
            "positionIdx": params["positionIdx"] if "positionIdx" in params else 0,
        }
        apiUrl = "/v5/order/create"
        try:
            response = self._signedRequest(method='POST', path=apiUrl, query=body, auth=True)
            return self._parseCreateOrder(response)
        except Exception as e:
            raise e
    
    def fetch_order(self, id, symbol=None):
        apiUrl = "/v5/order/realtime"
        queryParams = {"category": self.category, "orderId": id}
        try:
            resp = resp = self._signedRequest(method='GET', path=apiUrl, query=queryParams, auth=True)
            return resp #self._parseOrder(resp)
        except Exception as e:
            raise e

    def fetch_open_orders(self, symbol=None,  kwargs=None):
        apiUrl = "/v5/order/realtime"
        queryParams = {"category": self.category, "symbol": self._getSymbol(symbol)}
        try:
            resp = resp = self._signedRequest(method='GET', path=apiUrl, query=queryParams, auth=True)
            return self._parseOpenOrders(resp)
        except Exception as e:
            raise e
        
    def cancel_order(self, id, symbol=None, params={}):
        apiUrl = "/v5/order/cancel"
        queryParams = {"category": self.category, "orderId": id, "symbol": self._getSymbol(symbol)}
        try:
            resp = self._signedRequest(method='POST', path=apiUrl, query=queryParams, auth=True)
            return self._parseCreateOrder(resp)
        except Exception as e:
            raise e

    def fetch_ticker(self, symbol: str, params={}) -> baseTypes.Ticker:
        apiUrl = "/v5/market/tickers"
        queryParams = {"symbol": self._getSymbol(symbol), "category": self.category}
        try:
            resp = self._signedRequest(method='GET', path=apiUrl, query=queryParams)
            return resp # parse this response into Ticker
        except Exception as e:
            raise e
    
    def fetch_balance(self, params={}) -> baseTypes.Balances:
        apiUrl = '/v5/account/wallet-balance'
        queryParams = {"accountType": self.account_type}
        try:
            resp = self._signedRequest(method='GET', path=apiUrl, query=queryParams, auth=True)
            return self._parseBalance(resp)
        except WrongAccountType as e:
            apiUrl = "/v5/asset/transfer/query-account-coins-balance"
            queryParams = {"accountType": "SPOT"}
            try:
                resp = self._signedRequest(method='GET', path=apiUrl, query=queryParams, auth=True)
                return self._parseBalance(resp)
            except Exception as e:
                raise e
        except Exception as e:
            raise e
    
    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        apiUrl = '/v5/execution/list'
        queryParams = {"category": self.category}
        if symbol:
            queryParams["symbol"] = self._getSymbol(symbol)
        if since:
            queryParams["startTime"] = since
        if limit:
            queryParams["limit"] = limit
        if 'endTime' in params:
            queryParams["endTime"] = params['endTime']
        try:
            resp = self._signedRequest(method='GET', path=apiUrl, query=queryParams, auth=True)
            return self._parseTrades(resp)
        except Exception as e:
            raise e
        
    def fetch_order_book(self, symbol: str, limit=None, params={}) -> baseTypes.OrderBook:
        apiUrl = "/v5/market/orderbook"
        queryParams = {"symbol": self._getSymbol(symbol), "category": self.category}
        if limit is not None:
            queryParams["limit"] = int(limit)
        queryParams.update(params)
        try:
            resp = self._signedRequest(method='GET', path=apiUrl, query=queryParams)
            return self._parseOrderbook(resp)
        except Exception as e:
            raise e
        
    def fetch_ohlcv(self, symbol: str, timeframe='1m', since = None, limit = None, params={}):
        raise NotImplementedError("Subclasses must implement this method")