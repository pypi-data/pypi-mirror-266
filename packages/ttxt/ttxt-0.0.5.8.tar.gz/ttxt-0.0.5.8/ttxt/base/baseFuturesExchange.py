class BaseFuturesExchange:
    def __init__(self, key, secret, **kwargs):
        self.key = key
        self.secret = secret
        self.additional_params = kwargs

    def fetch_ticker(self, symbol):
        raise NotImplementedError("Subclasses must implement this method")
    
    def fetch_ohlcv(self, symbol: str, timeframe='1m', since = None, limit = None, params={}):
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
    
    def set_leverage(self, leverage, symbol, params={}):
        raise NotImplementedError("Subclasses must implement this method")
    
    def fetch_order_book(self, symbol: str, limit=None, params={}):
        raise NotImplementedError("Subclasses must implement this method")