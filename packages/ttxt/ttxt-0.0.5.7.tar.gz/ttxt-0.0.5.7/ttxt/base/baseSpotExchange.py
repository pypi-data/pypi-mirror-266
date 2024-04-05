class BaseSpotExchange:
    def __init__(self, key, secret, **kwargs):
        self.key = key
        self.secret = secret
        self.additional_params = kwargs

    def fetch_ticker(self, symbol):
        raise NotImplementedError("Subclasses must implement this method")
    
    def fetch_ohlcv(self, symbol, interval, params={}):
        raise NotImplementedError("Subclasses must implement this method")
    
    def fetch_balance(self, symbol):
        raise NotImplementedError("Subclasses must implement this method")

    def create_order(self, symbol, quantity, price, order_type):
        raise NotImplementedError("Subclasses must implement this method")
    
    def fetch_order(self, id: str, symbol = None, params={}):
        raise NotImplementedError("Subclasses must implement this method")
    
    def fetch_open_orders(self, symbol=None,  kwargs=None):
        raise NotImplementedError("Subclasses must implement this method")
    
    def cancel_order(self, id: str):
        raise NotImplementedError("Subclasses must implement this method")
    
    def fetch_my_trades(self, symbol, startTime, endTime, limit, params={}):
        raise NotImplementedError("Subclasses must implement this method")