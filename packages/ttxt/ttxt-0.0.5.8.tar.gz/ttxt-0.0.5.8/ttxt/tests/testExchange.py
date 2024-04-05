import os, sys, json
from dotenv import load_dotenv

load_dotenv()

DIR_NAME = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(DIR_NAME))
sys.path.append(root)

import ttxt

def getTtxtExchange(exchangeName):
    if exchangeName == "gateFutures":
        print("returned gateFuture")
        return ttxt.gateFutures(key=os.getenv("KEY"), secret=os.getenv("SECRET"))
    if exchangeName == "bybitFutures":
        print("returned bybitFutures")
        return ttxt.bybitFutures(key=os.getenv("KEY"), secret=os.getenv("SECRET"))
    if exchangeName == "bitgetFutures":
        print("returned bitgetFutures")
        return ttxt.bitgetFutures(key=os.getenv("KEY"), secret=os.getenv("SECRET"), password=os.getenv("PASSWORD"))
    if exchangeName == "bitget":
        print("returned bitget")
        return ttxt.bitget(key=os.getenv("KEY"), secret=os.getenv("SECRET"), password=os.getenv("PASSWORD"))
    if exchangeName == "kucoin":
        print("returned kucoin")
        return ttxt.kucoin(key=os.getenv("KEY"), secret=os.getenv("SECRET"), password=os.getenv("PASSWORD"))
    if exchangeName == "binance":
        print("returned binance")
        return ttxt.binance(key=os.getenv("KEY"), secret=os.getenv("SECRET"))
    if exchangeName == "bingx":
        print("returned bingx")
        return ttxt.bingx(key=os.getenv("KEY"), secret=os.getenv("SECRET"))
    if exchangeName == "biconomy":
        print("returned biconomy")
        return ttxt.biconomy(key=os.getenv("KEY"), secret=os.getenv("SECRET"))
    if exchangeName == "mexc":
        print("returned mexc")
        return ttxt.mexc(key=os.getenv("KEY"), secret=os.getenv("SECRET"))
    if exchangeName == "gate" or exchangeName == "gateio":
        print("returned gate")
        return ttxt.gateio(key=os.getenv("KEY"), secret=os.getenv("SECRET"))
    if exchangeName == "bybit":
        print("returned bybit")
        return ttxt.bybit(key=os.getenv("KEY"), secret=os.getenv("SECRET"))
    if exchangeName == "okx":
        print("returned okx")
        return ttxt.okx(key=os.getenv("KEY"), secret=os.getenv("SECRET"), password=os.getenv("PASSWORD"))
    if exchangeName == "huobi":
        print("returned huobi")
        return ttxt.huobi(key=os.getenv("KEY"), secret=os.getenv("SECRET"))
    if exchangeName == "bitmart":
        print("returned bitmart")
        return ttxt.bitmart(key=os.getenv("KEY"), secret=os.getenv("SECRET"), password=os.getenv("PASSWORD"))
    if exchangeName == "cryptocom":
        print("returned cryptocom")
        return ttxt.cryptocom(key=os.getenv("KEY"), secret=os.getenv("SECRET"))
    else:
        print(f"Exchange not supported: {exchangeName}")
        return None

def test(exchangeName="", params={}):
    ttxtExchange = getTtxtExchange(exchangeName)
    # ttxtExchange = ttxt.gateFutures(key=os.getenv("KEY"), secret=os.getenv("SECRET"))

    if "ticker" in params and params["ticker"]:
        print("testing ticker...")
        try:
            resp = ttxtExchange.fetch_ticker(tickerToTest)
            print(resp)
        except Exception as e:
            print("ticker could not be fetched")
            print(e)
    if "balance" in params and params["balance"]:
        print("testing balance...")
        try:
            resp = ttxtExchange.fetch_balance()
            print(resp)
        except Exception as e:
            print("balance could not be fetched")
            print(e)
    if "createOrder" in params and params["createOrder"]:
        print("testing create order...")
        try:
            resp = ttxtExchange.create_order(symbol=tickerToTest, order_type="limit", amount="5", side="sell", price=5)
            print(f"createOrder response: {resp}")
        except Exception as e:
            print("order could not be created")
            print(e)
    if "createLimitOrder" in params and params["createLimitOrder"]:
        print("testing limit create order...")
        try:
            resp = ttxtExchange.create_limit_order(symbol=tickerToTest, amount=50, side="buy", price=0.20)
            print(f"createLimitOrder response: {resp}")
        except Exception as e:
            print("limit order could not be created")
            print(e)
    if "createMarketSellOrder" in params and params["createMarketSellOrder"]:
        print("testing market sell create order...")
        try:
            resp = ttxtExchange.create_market_sell_order(symbol=tickerToTest, amount=0.001)
            print(f"createMarketSellOrder response: {resp}")
        except Exception as e:
            print("market sell order could not be created")
            print(e)
    if "createMarketBuyOrder" in params and params["createMarketBuyOrder"]:
        print("testing market buycreate order...")
        try:
            resp = ttxtExchange.create_market_buy_order(symbol=tickerToTest, amount=0.001)
            print(f"createMarketBuyOrder response: {resp}")
        except Exception as e:
            print("market buy order could not be created")
            print(e)
    if "create_market_order" in params and params["create_market_order"]:
        print("testing create market order...")
        try:
            resp = ttxtExchange.create_market_order(symbol=tickerToTest, side="sell", amount=1)
            print(f"create_market_order response: {resp}")
        except Exception as e:
            print("market order could not be created")
            print(e)
    if "fetchOrder" in params and params["fetchOrder"]:
        print("testing fetch order...")
        try:
            resp = ttxtExchange.fetch_order(id=45577069671, symbol=tickerToTest)
            print(f"fetchOrder response: {resp}")
        except Exception as e:
            print("order could not be fetched")
            print(e)
    if "cancelOrder" in params and params["cancelOrder"]:
        print("testing cancel order...")
        try:
            resp = ttxtExchange.cancel_order(id=698922787, symbol=tickerToTest)
            print(f"cancelOrder response: {resp}")
        except Exception as e:
            print("order could not be canceled")
            print(e)
    if "fetchOpenOrders" in params and params["fetchOpenOrders"]:
        print("testing open orders...")
        try:
            resp = ttxtExchange.fetch_open_orders(symbol=tickerToTest)
            print(f"total open orders: {len(resp)}")
            print(f"fetchOpenOrders response: {resp}")
        except Exception as e:
            print("OpenOrders could not be fetched")
            print(e)
    if "cancelAllOrders" in params and params["cancelAllOrders"]:
        print("testing open orders...")
        try:
            resp = ttxtExchange.fetch_open_orders(symbol=tickerToTest)
            print(f"total open orders: {len(resp)}")
            for order in resp:
                ttxtExchange.cancel_order(id=order['id'], symbol=tickerToTest)
            print(f"cancelAllOrders response: {resp}")
        except Exception as e:
            print("OpenOrders could not be fetched")
            print(e)
    if "setLeverage" in params and params["setLeverage"]:
        print("testing set leverage...")
        try:
            resp = ttxtExchange.set_leverage(symbol=tickerToTest, leverage=10)
            print(f"set leverage response: {resp}")
        except Exception as e:
            print("leverage could not be set")
            print(e)
    if "ohlcv" in params and params["ohlcv"]:
        print("testing ohlcv...")
        try:
            resp = ttxtExchange.fetch_ohlcv(symbol=tickerToTest, interval="hour", size=10)
            print(f"ohlcv response: {resp}")
        except Exception as e:
            print("leverage could not be set")
            print(e)
    if "orderbook" in params and params["orderbook"]:
        print("testing orderbook...")
        try:
            resp = ttxtExchange.fetch_order_book(symbol=tickerToTest, limit=100)
            print(f"orderbook response: {resp}")
        except Exception as e:
            print("orderbook could not be fetched")
            print(e)
    if "candlestick" in params and params["candlestick"]:
        print("testing candlestick...")
        try:
            resp = ttxtExchange.fetch_ohlcv(symbol=tickerToTest, timeframe='1h', limit=1)
            print(f"candlestick response: {resp}")
            print(f"candlestick response len: {len(resp)}")
        except Exception as e:
            print("candlesticks could not be fetched")
            print(e)
    if "myTrades" in params and params["myTrades"]:
        print("testing myTrades...")
        try:
            resp = ttxtExchange.fetch_my_trades(symbol=tickerToTest, since=1710863600671)
            print(resp)
        except Exception as e:
            print("myTrades could not be fetched")
            print(e)


if __name__ == "__main__":
    tickerToTest = "GALA/USDT"
    testingParams = {"ticker": False, 
                     "balance": True, 
                     "ohlcv": False, 
                     "createOrder": False, 
                     "fetchOrder": False, 
                     "cancelOrder": False, 
                     "fetchOpenOrders": False, 
                     "setLeverage": False, 
                     "createLimitOrder": False,
                     "createMarketSellOrder": False, 
                     "createMarketBuyOrder": False, 
                     "orderbook": False, 
                     "candlestick": False,
                     "create_market_order": False, 
                     "cancelAllOrders": False, 
                     "myTrades": False}
    test(params=testingParams, exchangeName="bybit")
