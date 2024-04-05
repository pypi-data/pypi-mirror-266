import hmac
import base64
import hashlib
import json
import time
import requests
from urllib.parse import urlencode
from ttxt.base import baseFuturesExchange
from ttxt.types import baseTypes
# Example of an exchange requiring a password
'''
Sample 
kwargs = {
    "productType": "",
    "marginMode": "",
    "marginCoin": ""
}
'''
class bitgetFutures(baseFuturesExchange.BaseFuturesExchange):
    def __init__(self, key, secret, password, **kwargs):
        super().__init__(key, secret, **kwargs)
        self.password = password
        self.domain_url = "https://api.bitget.com"
        self.productType =  kwargs["productType"] if "productType" in kwargs else "USDT-FUTURES"
        self.marginMode = kwargs["marginMode"] if "marginMode" in kwargs else "isolated"
        self.marginCoin = kwargs["marginCoin"] if "marginCoin" in kwargs else "USDT"
        self.success_sode = '00000'

    def sign(self, message):
        mac = hmac.new(bytes(self.secret, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d)

    def pre_hash(self, timestamp, method, request_path, queryString, body=None):
        if not body:
            return str(timestamp) + str.upper(method) + request_path + queryString
        return str(timestamp) + str.upper(method) + request_path + body

    def parse_params_to_str(self, params):
        params = [(key, val) for key, val in params.items()]
        params.sort(key=lambda x: x[0])
        url = '?' + urlencode(params)
        if url == '?':
            return ''
        return url

    def _signedRequest(self, method, request_path, queryString, body):
        timeMs = int(time.time()) *1000
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
            try:
                params = body
                body = ""
                request_path = request_path + self.parse_params_to_str(params) # Need to be sorted in ascending alphabetical order by key
                signature = self.sign(self.pre_hash(timeMs, "GET", request_path, str(body)))

                headers = {"ACCESS-KEY": self.key, "ACCESS-SIGN": signature, "ACCESS-PASSPHRASE": self.password, "ACCESS-TIMESTAMP": str(timeMs), "locale": "en-US", "Content-Type": "application/json"}
                url = self.domain_url+request_path
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
        parsedBal = {}
        parsedBal["free"] = balData.get("available", None)
        parsedBal["total"] = balData.get("total", None)
        parsedBal["unrealisedPnl"] = balData.get("unrealised_pnl", None)
        parsedBal["currency"] = balData.get("currency", None)
        return parsedBal


    ## Exchange functions 
    def fetch_ticker(self, symbol):
        print(f"Fetching ticker for {symbol} with password {self.password}")
        
    def create_order(self, symbol, type, side, amount, price=None, params={}):
        try:
            if type == "market":
                body = {
                    "symbol": symbol,
                    "productType": self.productType,
                    "marginMode": self.marginMode,
                    "marginCoin":self.marginCoin,
                    "size": amount,
                    "side": side,
                    "tradeSide": params["tradeSide"] if "tradeSide" in params else "",
                    "orderType": "market",
                    "force": params["force"] if "force" in params else "",
                    "reduceOnly": params["reduceOnly"] if "reduceOnly" in params else "NO",
                    "presetStopSurplusPrice": params["tpPrice"] if "tpPrice" in params else "",
                    "presetStopLossPrice": params["slPrice"] if "slPrice" in params else "",
                }
            elif type == "limit":
                body = {
                    "symbol": symbol,
                    "productType": self.productType,
                    "marginMode": self.marginMode,
                    "marginCoin":self.marginCoin,
                    "size": amount,
                    "price": price,
                    "side": side,
                    "tradeSide": params["tradeSide"] if "tradeSide" in params else "",
                    "orderType": "market",
                    "force": params["force"] if "force" in params else "",
                    "reduceOnly": params["reduceOnly"] if "reduceOnly" in params else "NO",
                    "presetStopSurplusPrice": params["tpPrice"] if "tpPrice" in params else "",
                    "presetStopLossPrice": params["slPrice"] if "slPrice" in params else "",
                }
            # body = '{"symbol":' + '\"' + demoSymbol + '",' + '\"marginCoin":"SUSDT","side":"open_long","orderType":"market","size":' + '\"' + str(quantity) + '\"}'
            apiUrl = "/api/v2/mix/order/place-order"
            response = self._signedRequest('POST', apiUrl, None, body)
            return response
        except Exception as e:
            raise e
        
    # def fetch_ticker(self, symbol: str, params={}) -> baseTypes.Ticker:
    #     apiUrl = "/api/v2/mix/market/ticker"
    #     params = {
    #         "symbol": symbol,
    #         "productType": self.productType
    #     }
    #     resp = self._unsignedRequest('GET', apiUrl, params=params)
    #     return resp # parse this response into Ticker
    
    def fetch_balance(self, params={}) -> baseTypes.Balances:
        pass

    def fetch_account(self, symbol, params={}):
        try:
            body = {
                "symbol": symbol,
                "productType": self.productType,
                "marginCoin":self.marginCoin,
            }
            apiUrl = "/api/v2/mix/account/account"
            response = self._signedRequest('GET', apiUrl, None, body)
            if response['code'] == self.success_sode:
                return response['data']
            return response
        except Exception as e:
            raise e
        
    def fetch_accounts(self, params={}):
        try:
            body = {
                "productType": self.productType,
            }
            apiUrl = "/api/v2/mix/account/accounts"
            response = self._signedRequest('GET', apiUrl, None, body)
            if response['code'] == self.success_sode:
                return response['data']
            return response
        except Exception as e:
            raise e
        
    def fetch_position(self, symbol, params={}):
        try:
            body = {
                "symbol": symbol,
                "productType": self.productType,
                "marginCoin":self.marginCoin,
            }
            apiUrl = "/api/v2/mix/position/single-position"
            response = self._signedRequest('GET', apiUrl, None, body)
            if response['code'] == self.success_sode:
                return response['data']
            return response
        except Exception as e:
            raise e

    def fetch_positions(self, params={}):
        try:
            body = {
                "productType": self.productType,
                "marginCoin": self.marginCoin,
            }
            apiUrl = "/api/v2/mix/position/all-position"
            response = self._signedRequest('GET', apiUrl, None, body)
            if response['code'] == self.success_sode:
                return response['data']
            return response
        except Exception as e:
            raise e

    def fetch_ticker(self, symbol):
        apiUrl = "/api/v2/mix/market/ticker"
        params = {
            "symbol": symbol,
            "productType": self.productType
        }
        resp = self._unsignedRequest('GET', apiUrl, params=params)
        return resp

    def set_leverage(self, symbol, leverage):
        apiUrl = "/api/v2/mix/account/set-leverage"
        params = {
            "symbol": symbol,
            "productType": self.productType,
            "marginCoin": self.marginCoin,
            "leverage": leverage,
            "holdSide": "long"
        }
        response_long = self._signedRequest('POST', apiUrl, None, params)
        params["holdSide"] = "short"
        response_short = self._signedRequest('POST', apiUrl, None, params)
        return True

    def cancel_order(self, id, params={}):
        pass

    def fetch_ohlcv(self, symbol, timeframe, startTime, endTime=None, limit=200):
        params = {
            'symbol': symbol,
            'granularity': timeframe,
            'startTime': startTime,
            'endTime': endTime,
            'limit': limit,
            'productType': 'usdt-futures'
        }
        if endTime is None and limit is None:
            print("endTime or limit must be specified")
            return []
        if endTime is None:
            params.pop('endTime')
        if limit is None:
            params.pop('limit')

        full_url = f"https://api.bitget.com/api/v2/mix/market/history-candles?"+'&'.join([f'{k}={v}' for k, v in params.items()])
        retry = True
        while retry:
            response = requests.get(full_url)
            if response.status_code == 200:
                candle_data = json.loads(response.content)['data']
                if len(candle_data) > 0:
                    return candle_data
            else:
                break
        return []