from utils.ExchangeUtil import ExchangeInterface
from quantLogic.OneHourDownNotify import notifyByLastHour

import time
import datetime
import pytz

def testDownPercent() :
    exchange = ExchangeInterface.initOkxExchange()
    notifyDict = dict()
    currency = 'CTC/USDT'
    ohlcvData = ExchangeInterface.getOHLCVDataByCurrency(exchange, currency, '1d')
    notifyByLastHour(ohlcvData, currency, notifyDict)

"""
:return: 测试结果：使用一分钟左右跑完整个过程
"""
def testRunTime():
    exchange = ExchangeInterface.initOkxExchange()
    listCurrency = ExchangeInterface.getAllCurrencyList(exchange)
    timeStampBegin = time.time()
    print("timeBegin:", datetime.datetime.fromtimestamp(int(timeStampBegin), pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S'))
    notifyDict = dict()
    for currency in listCurrency:
        ohlcvData = ExchangeInterface.getOHLCVDataByCurrency(exchange, currency, '1h')
        notifyByLastHour(ohlcvData, currency, notifyDict)
    timeStampEnd = time.time()
    print("timeEnd:", datetime.datetime.fromtimestamp(int(timeStampEnd), pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S'))
