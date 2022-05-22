import ccxt
import datetime
import pytz

from utils.QuantLogging import Log

debugLogger = Log('debug', '%(message)s', 'tradeAbnormal')

exchangeOkx = ccxt.okx({
    'apiKey': '',
    'secret': '',
    'timeout': 30000,
    'enableRateLimit': True,
})

exchangeBinance = ccxt.binance({
    'apiKey': '',
    'secret': '',
    'timeout': 30000,
    'enableRateLimit': True,
})

def getMarkets(exchange):
    markets = exchange.load_markets()
    return markets


def getAllCurrencyList(exchange):
    listCurrency = []
    markets = exchange.load_markets()
    for info in markets.values():
        if info['base'].find('UP') == -1 and info['base'].find('DOWN') == -1:
            if info['quote'] == 'USDT' and info['strike'] is None and (info['settle'] == ''
                   or info['settle'] is None) and (info['settleId'] == '' or info['settleId'] is None):
                        listCurrency.append(info['symbol'])
    return listCurrency

def testOHLCV(exchange):
    if exchange.has['fetchOHLCV']:
        ohlcvData = exchange.fetch_ohlcv('BICO/USDT', '1d', 1630462892000, 1000)    #2021-9-2(1630462892000)
        for info in ohlcvData:
            print("info:", info)
        print('size:', len(ohlcvData))

def testTicker(exchange):
    if exchange.has['fetchTicker']:
        print(exchange.fetch_ticker('SOL/USDT'))  # ticker for SOL/USDT

def testOrderBook(exchange):
    data = exchange.fetch_order_book('WGRT/USDT')
    print(data)
    print("len:", len(data['bids']))

# timeStamp：毫秒级时间戳
def timeStampFormatShanghaiTime(timeStamp):
    timeStamp = float(timeStamp / 1000)
    shanghaiTime = datetime.datetime.fromtimestamp(int(timeStamp), pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
    return shanghaiTime

def testExchangeAPI():
    #listCurrency = getAllCurrencyList(exchangeBinance)
    #market = getMarkets(exchangeBinance)
    #testOHLCV(exchangeOkx)
    testOrderBook(exchangeOkx)
    #testTicker()

if __name__ == '__main__':
    testExchangeAPI()
