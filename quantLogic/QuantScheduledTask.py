import json
import os
import sys
import time

cwdStr = os.getcwd() + '/../'
sys.path.append(cwdStr)

from math import floor
from utils.QuantLogging import Log
from utils.ExchangeUtil import ExchangeInterface, OHLCVIndex
from utils.TimeUtil import TimeInterface
from apscheduler.schedulers.background import BackgroundScheduler

def recordBaseHourAndQuoteVol():
    fileName = TimeInterface().getOffsetDayStr(time.time()*1000, -1, '%Y.%m.%d')
    baseVolLogger = Log(fileName + '-base', '%(message)s', 'baseVol/')
    quoteVolLogger = Log(fileName + '-quote', '%(message)s', 'quoteVol/')
    exchange = ExchangeInterface().initOkxExchange()
    listCurrency = ExchangeInterface().getAllCurrencyList(exchange)
    baseVolDict = dict()
    quoteVolDict = dict()
    for currency in listCurrency:
        tickerResult = ExchangeInterface().getTickerByCurrency(exchange, currency)
        baseVolDict[currency] = floor(tickerResult['baseVolume'])    #记录每一个币种过去24小时的交易量
        quoteVolDict[currency] = floor(tickerResult['quoteVolume'])

    baseVolLogStr = "{}".format(json.dumps(baseVolDict))
    baseVolLogger.info(baseVolLogStr)

    quoteVolLoggerStr = "{}".format(json.dumps(quoteVolDict))
    quoteVolLogger.info(quoteVolLoggerStr)

def recordTwelveClockData():
    exchange = ExchangeInterface().initOkxExchange()
    listCurrency = ExchangeInterface().getAllCurrencyList(exchange)
    outputCurrencyDict = dict()
    for currency in listCurrency:
        ohlcvData = ExchangeInterface().getOHLCVDataByCurrency(exchange, currency, '1h')
        lastHourData = ohlcvData[len(ohlcvData) - 1]  # 取最后一根k线数据
        upPercent = ((lastHourData[OHLCVIndex().highest] - lastHourData[OHLCVIndex().open]) / lastHourData[OHLCVIndex().open]) * 100
        if upPercent > 25:
            outputCurrencyDict[currency] = floor(upPercent)

    outputCurrencyDict = sorted(outputCurrencyDict.items(), key=lambda item: item[1], reverse=True)
    recordStr = TimeInterface().timeStampToShanghaiTime(time.time()*1000, '%Y-%m-%d') + '：'
    for item in outputCurrencyDict:
        recordStr += "{}({})，".format(item[0], item[1])

    if recordStr != '':
        recordStr = recordStr.rstrip('，')
        twelveDataLogger = Log('twelveData', '%(message)s', 'twelveData')
        twelveDataLogger.info(recordStr)

'''
记录一天涨幅超过60%的币种
'''
def findAbnormalCurrency():
    abnormalCurrencyLogger = Log('AbnormalCurrencyList', '%(message)s', 'tradeAbnormal')
    exchange = ExchangeInterface().initOkxExchange()
    listCurrency = ExchangeInterface().getAllCurrencyList(exchange)
    beginTimeStamp = 1627179692000 #2021年7月25号
    limit = 500
    abnormalCurrencyDict = dict()
    for currency in listCurrency:
        ohlcvData = ExchangeInterface().getOHLCVDataByCurrency(exchange, currency, '1d', beginTimeStamp, limit)
        maxPercent = 50         #涨幅
        isMark = False
        indexOfKLine = 0        #维护第一天上市涨幅不算
        for data in ohlcvData:
            upPercent = floor((data[OHLCVIndex().highest] / data[OHLCVIndex().open] - 1) * 100)
            if upPercent > maxPercent and indexOfKLine != 0:
                maxPercent = upPercent
                isMark = True
            indexOfKLine += 1
        if isMark:
            abnormalCurrencyDict[currency] = maxPercent

    abnormalCurrencyStr = "{}".format(json.dumps(abnormalCurrencyDict))
    abnormalCurrencyLogger.info(abnormalCurrencyStr)

def initTask():
    scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(recordTwelveClockData, 'cron', hour=0, minute=35)         #每天0点35分执行任务
    scheduler.add_job(recordBaseHourAndQuoteVol, 'cron', hour=0, minute=1)      #记录前一天（24小时）的交易量和交易额
    scheduler.start()

if __name__ == '__main__':
    initTask()
    #findAbnormalCurrency()