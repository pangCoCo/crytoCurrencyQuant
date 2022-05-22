import os
import sys
import time
from math import floor
from apscheduler.schedulers.background import BackgroundScheduler

cwdStr = os.getcwd() + '/../'
sys.path.append(cwdStr)

from utils.ExchangeUtil import OHLCVIndex
from utils.ExchangeUtil import ExchangeInterface
from utils.TimeUtil import TimeInterface
from utils.UserInfo import wuchuandingInfo
from utils.FunctionUtil import CommonFunction
from utils.QuantLogging import Log

class OneHourDownNotify:
    def __init__(self):
        self.oneHourDownLogger = Log('oneHourDownNotify', '%(message)s', 'oneHourDownNotify/')
        self.notifyDictOfOne = dict()                       # 维护一小时内通知的阀值
        self.recordCurHourDictOfOne = {'time': TimeInterface().getCurTimeStr()}

    def notifyByLastHour(self, exchange, ohlcvData, currency):
        if len(ohlcvData) == 0:
            return

        lastHourData = ohlcvData[len(ohlcvData) - 1]    #取最后一根k线数据
        downPercent = ((lastHourData[OHLCVIndex().open] - lastHourData[OHLCVIndex().lowest]) / lastHourData[OHLCVIndex().open]) * 100
        notifyThreshold = 6                             #币安通知阀值
        if exchange.name == 'OKX':
            notifyThreshold = 10                        #初始通知阀值
        notifyDictKey = exchange.name + currency
        if notifyDictKey in self.notifyDictOfOne:
            notifyThreshold = self.notifyDictOfOne[notifyDictKey]

        if downPercent > notifyThreshold:
            self.notifyDictOfOne[notifyDictKey] = notifyThreshold + 6  #阀值+6
            msgText = "{}，{}：跌了{}%".format(exchange.name, currency, floor(downPercent))
            desp = "{}：time：{}，open：{}，lowest：{}，跌了{}%".format(currency
                        , TimeInterface().timeStampToShanghaiTime(lastHourData[OHLCVIndex().timeStamp])
                        , lastHourData[OHLCVIndex().open], lastHourData[OHLCVIndex().lowest], floor(downPercent))
            CommonFunction().weiXinNotify(wuchuandingInfo().token, msgText, desp)

    def notifyByExchange(self, exchange, listCurrency):
        if self.recordCurHourDictOfOne['time'] != TimeInterface().getCurTimeStr():
            self.notifyDictOfOne.clear()
            self.recordCurHourDictOfOne['time'] = TimeInterface().getCurTimeStr()

        for currency in listCurrency:
            ohlcvData = ExchangeInterface().getOHLCVDataByCurrency(exchange, currency, '1h')
            self.notifyByLastHour(exchange, ohlcvData, currency)

        loggerStr = "{}, oneHourDownNotify logger time:{}".format(exchange.name, TimeInterface().timeStampToShanghaiTime((time.time() * 1000)))
        self.oneHourDownLogger.info(loggerStr)

    def oneHourDownNotifyByOKX(self):
        self.oneHourDownLogger.info("oneHourDownNotify OKX come in")
        exchangeOKX = ExchangeInterface().initOkxExchange()
        listCurrency = ExchangeInterface().getAllCurrencyList(exchangeOKX)
        scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
        scheduler.add_job(self.notifyByExchange, 'cron', hour='7-23', minute='*/3', args=[exchangeOKX, listCurrency])
        scheduler.start()

    def oneHourDownNotifyByBinance(self):
        self.oneHourDownLogger.info("oneHourDownNotify Binance come in")
        exchangeBinance = ExchangeInterface().initBinanceExchange()
        listCurrency = ExchangeInterface().getAllCurrencyList(exchangeBinance)
        scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
        scheduler.add_job(self.notifyByExchange, 'cron', hour='7-23', minute='*/1', args=[exchangeBinance, listCurrency])
        scheduler.start()

if __name__ == '__main__':
    OneHourDownNotify().oneHourDownNotifyByOKX()
    OneHourDownNotify().oneHourDownNotifyByBinance()