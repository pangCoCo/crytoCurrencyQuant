import ccxt

class ExchangeInterface:

    def initOkxExchange(self):
        exchange = ccxt.okx({
            'apiKey': '',
            'secret': '',
            'timeout': 30000,
            'enableRateLimit': True,
        })
        return exchange

    def initBinanceExchange(self):
        exchange = ccxt.binance({
            'apiKey': '',
            'secret': '',
            'timeout': 30000,
            'enableRateLimit': True,
        })
        return exchange

    """
    :return: 获取交易所下的所有currency的币种名称
    """
    def getAllCurrencyList(self, exchange):
        listCurrency = []
        markets = exchange.load_markets()
        for info in markets.values():
            if info['base'].find('UP') == -1 and info['base'].find('DOWN') == -1:
                if info['quote'] == 'USDT' and info['strike'] is None and (info['settle'] == ''
                       or info['settle'] is None) and (info['settleId'] == '' or info['settleId'] is None):
                    listCurrency.append(info['symbol'])
        return listCurrency

    """
    :param time: 1m，1h，1d
    :return: 获取currency的k线数据
    """
    def getOHLCVDataByCurrency(self, exchange, currency, time, since=None, limit=None):
        ohlcvData = []
        try:
            if exchange.has['fetchOHLCV']:
                ohlcvData = exchange.fetch_ohlcv(currency, time, since, limit)
        except ccxt.NetworkError as e:
            print(exchange.id, 'fetch_ohlcv failed due to a network error:', str(e))
        except ccxt.ExchangeError as e:
            print(exchange.id, 'fetch_ohlcv failed due to exchange error:', str(e))
        except Exception as e:
            print(exchange.id, 'fetch_ohlcv failed with:', str(e))
        return ohlcvData

    """
    :return: past 24 hours data data
    """
    def getTickerByCurrency(self, exchange, currency):
        if exchange.has['fetchTicker']:
            tickerResult = exchange.fetch_ticker(currency)
            return tickerResult

    def getOrderBookByCurrency(self, exchange, currency):
        return exchange.fetch_order_book(currency)


class OHLCVIndex:
    timeStamp = 0
    open = 1
    highest = 2
    lowest = 3
    closing = 4
    volume = 5