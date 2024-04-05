import hmac
import base64
import hashlib
import json
import time
import requests
from datetime import datetime as dt
from ttxt.base import baseFuturesExchange
from ttxt.types import baseTypes
# Requests will use simplejson if available.
try:
    from simplejson.errors import JSONDecodeError
except ImportError:
    from json.decoder import JSONDecodeError

'''
kwards = {
    "category": "",
    "recv_window": ""
}
'''
class bybitFutures(baseFuturesExchange.BaseFuturesExchange):
    def __init__(self, key, secret, **kwargs):
        super().__init__(key, secret, **kwargs)
        self.domain_url_testnet = "https://api-testnet.bybit.com"
        self.domain_url = "https://api.bybit.com"
        self.domain_url_2 = "https://api.bytick.com"
        self.prefix = "/api/v4"
        self.category = kwargs["category"] if "category" in kwargs else "linear"
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
                        #esp = client.send(r, timeout=60) 
                        resp = requests.get(path + f"?{req_params}", headers=headers)
                    else:
                        r = requests.get(path, headers=headers)
                    return resp.json()
                except Exception as e:
                    raise e
            if method == "POST":
                r = requests.post( path, data=req_params, headers=headers)
                return r.json()
            if method == "DELETE":
                r = requests.delete( path, data=req_params, headers=headers)
                return r.json()
    
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
    '''
    {"retCode":0,"retMsg":"OK","result":
    {"list":[{"totalEquity":"233.33780771","accountIMRate":"0","totalMarginBalance":"233.07030533",
    "totalInitialMargin":"0","accountType":"UNIFIED","totalAvailableBalance":"233.07030533",
    "accountMMRate":"0","totalPerpUPL":"0","totalWalletBalance":"233.07030533",
    "accountLTV":"0","totalMaintenanceMargin":"0",
    "coin":[{"availableToBorrow":"","bonus":"0","accruedInterest":"0","availableToWithdraw":"0.00000978",
        "totalOrderIM":"0","equity":"0.00000978","totalPositionMM":"0","usdValue":"0.02315849",
        "unrealisedPnl":"0","collateralSwitch":true,"spotHedgingQty":"0","borrowAmount":"0.000000000000000000",
        "totalPositionIM":"0","walletBalance":"0.00000978","cumRealisedPnl":"-0.00000598","locked":"0",
        "marginCollateral":true,"coin":"ETH"},
        {"availableToBorrow":"","bonus":"0","accruedInterest":"",
        "availableToWithdraw":"0.004","totalOrderIM":"0","equity":"0.004","totalPositionMM":"0",
        "usdValue":"0.00481953","unrealisedPnl":"0","collateralSwitch":false,"spotHedgingQty":"0",
        "borrowAmount":"0.000000000000000000","totalPositionIM":"0","walletBalance":"0.004",
        "cumRealisedPnl":"0","locked":"0","marginCollateral":false,"coin":"XCAD"},
        {"availableToBorrow":"","bonus":"0","accruedInterest":"0","availableToWithdraw":"232.52736215","totalOrderIM":"0","equity":"232.52736215","totalPositionMM":"0","usdValue":"232.56261562","unrealisedPnl":"0","collateralSwitch":true,"spotHedgingQty":"0","borrowAmount":"0.000000000000000000","totalPositionIM":"0","walletBalance":"232.52736215","cumRealisedPnl":"-0.07024754","locked":"0","marginCollateral":true,"coin":"USDT"},{"availableToBorrow":"","bonus":"0","accruedInterest":"0","availableToWithdraw":"24.0062","totalOrderIM":"0","equity":"24.0062","totalPositionMM":"0","usdValue":"0.74721405","unrealisedPnl":"0","collateralSwitch":true,"spotHedgingQty":"0","borrowAmount":"0.000000000000000000","totalPositionIM":"0","walletBalance":"24.0062","cumRealisedPnl":"-1.7438","locked":"0","marginCollateral":true,"coin":"GALA"}]}]},"retExtInfo":{},"time":1702038150602}
    '''
    # balData = {"free": {"USDT": 1010, "BTC": ""}, "total": {"USDT": 1010, "BTC": 0}, "unrealisedPnl": {"USDT": 1010, "BTC": 0}}
    def _parseBalance(self, balData):
        parsedBal = {"free": {}, "total": {}, "unrealisedPnl": {}}
        balDataResult = balData.get("result", None)
        balDatList = balDataResult.get("list", [])
        if len(balDatList) == 0:
            return parsedBal
        balDatList = balDatList[0].get("coin", [])
        if len(balDatList) == 0:
            return parsedBal
        for balDataEle in balDatList:
            parsedBal["free"][balDataEle["coin"]] = balDataEle.get("walletBalance", None)
            parsedBal["total"][balDataEle["coin"]] = balDataEle.get("equity", None)
            parsedBal["unrealisedPnl"][balDataEle["coin"]] = balDataEle.get("unrealisedPnl", None)
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

    '''
    {'retCode': 0, 'retMsg': 'OK', 'result': {'orderId': 'f3708d4e-24d6-4528-9037-764d03610479', 'orderLinkId': ''}, 
    'retExtInfo': {}, 'time': 1702055115208}
    '''
    def _parseOrder(self, order):
        parsedOrder = {}
        parsedOrder["id"] = order["orderId"]
        parsedOrder["symbol"] = self._getUserSymbol(order["contract"])
        parsedOrder["price"] = float(order["price"])
        parsedOrder["amount"] = float(order["size"])
        parsedOrder["side"] = "buy" if parsedOrder["amount"] > 0 else "sell"
        parsedOrder["timestamp"] = float(order["create_time"])
        parsedOrder["status"] = order["status"]
        parsedOrder["orderJson"] = json.dumps(order)
        return parsedOrder
    
    def _parseCreateorder(self, order):
        parsedOrder = {}
        parsedOrder["id"] = order["orderId"]
        parsedOrder["symbol"] = None
        parsedOrder["price"] = None
        parsedOrder["amount"] = None
        parsedOrder["side"] = None
        parsedOrder["timestamp"] = None
        parsedOrder["status"] = None
        parsedOrder["orderJson"] = json.dumps(order)
        return parsedOrder

    def _parseOpenOrders(self, orders):
        parsedOrderList = []
        for order in orders:
            parsedOrderList.append(self._parseOrder(order))
        return parsedOrderList

    '''
    {'retCode': 0, 'retMsg': 'OK', 'result': {'nextPageCursor': 'f3708d4e-24d6-4528-9037-764d03610479%3A1702055115208%2Cf3708d4e-24d6-4528-9037-764d03610479%3A1702055115208', 'category': 'linear', 'list': [{'symbol': 'BTCUSDT', 'orderType': 'Limit', 'orderLinkId': '', 'slLimitPrice': '0', 'orderId': 'f3708d4e-24d6-4528-9037-764d03610479', 'cancelType': 'UNKNOWN', 'avgPrice': '43832.1', 'stopOrderType': '', 'lastPriceOnCreated': '43832', 'orderStatus': 'Filled', 'takeProfit': '', 'cumExecValue': '43.8321', 'tpslMode': 'UNKNOWN', 'smpType': 'None', 'triggerDirection': 0, 'blockTradeId': '', 'isLeverage': '', 'rejectReason': 'EC_NoError', 'price': '43920', 'orderIv': '', 'createdTime': '1702055115208', 'tpTriggerBy': '', 'positionIdx': 0, 'timeInForce': 'GTC', 'leavesValue': '0', 'updatedTime': '1702055115209', 'side': 'Buy', 'smpGroup': 0, 'triggerPrice': '', 'tpLimitPrice': '0', 'cumExecFee': '0.02410766', 'leavesQty': '0', 'slTriggerBy': '', 'closeOnTrigger': False, 'placeType': '', 'cumExecQty': '0.001', 'reduceOnly': False, 'qty': '0.001', 'stopLoss': '', 'smpOrderId': '', 'triggerBy': ''}]}, 'retExtInfo': {}, 'time': 1702055320777}
    '''
    def _parseFetchedOrder(self, order):
        pass

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
            return self._parseCreateorder(response)
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
        queryParams = {"category": self.category}
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
            return resp #self._parseOrder(resp)
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
        except Exception as e:
            raise e
    
    def set_leverage(self, leverage, symbol, params={}):
        apiUrl = "/v5/position/set-leverage"
        queryParams = {"category": self.category, "symbol": self._getSymbol(symbol), "buyLeverage": str(leverage), "sellLeverage": str(leverage)}
        try:
            resp = self._signedRequest(method='POST', path=apiUrl, query=queryParams, auth=True)
            return resp
        except Exception as e:
            raise e

    ## extra functions
    def getInstrumentInfo(self, symbol):
        apiUrl = "/v5/market/instruments-info"
        queryParams = {"symbol": self._getSymbol(symbol), "category": self.category}
        try:
            resp = self._signedRequest(method='GET', path=apiUrl, query=queryParams)
            return resp # parse this response into Ticker
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