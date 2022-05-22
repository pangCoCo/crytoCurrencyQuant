import json
import os
import sys

cwdStr = os.getcwd() + '/../'
sys.path.append(cwdStr)

from math import floor
from apscheduler.schedulers.background import BackgroundScheduler
from utils.UserInfo import wuchuanruiInfo
from utils.ExchangeUtil import OHLCVIndex
from utils.FunctionUtil import CommonFunction
from utils.ExchangeUtil import ExchangeInterface
from utils.TimeUtil import TimeInterface
from utils.QuantLogging import Log

import time

class QuantTradeAbnormal:
    def __init__(self):
        self.outputFormat = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
        self.abnormalLogger = Log('quantTradeAbnormal', self.outputFormat, 'tradeAbnormal/')
        self.recordDataLogger = Log('abnormalData', self.outputFormat, 'tradeAbnormal/')
        self.oneDayBaseVolDict = dict()       # 一天的交易量
        self.oneDayQuoteVolDict = dict()
        self.notifyByCurHourDict = dict()     # 维护币种在当前小时有没有被通知过
        self.abnormalCurrencyDict = dict()    # 曾经一天出现过暴涨的币种
        self.recordCurDayDict = {'time': TimeInterface().getCurTimeStr()}
        self.init24HourBaseVolDict()
        self.init24HourQuoteVolDict()

    def init24HourBaseVolDict(self):
        fileName = TimeInterface().getOffsetDayStr(time.time()*1000, -1, '%Y.%m.%d') + '-base.log'
        filePath = os.getcwd() + '/../logs/' + 'baseVol/' + fileName
        data = CommonFunction().getJsonByFileName(filePath)
        for key in data:
            self.oneDayBaseVolDict[key] = data[key]
        self.abnormalLogger.info("init24HourBaseVolDict succ:{}".format(json.dumps(self.oneDayBaseVolDict)))

    def init24HourQuoteVolDict(self):
        fileName = TimeInterface().getOffsetDayStr(time.time() * 1000, -1, '%Y.%m.%d') + '-quote.log'
        filePath = os.getcwd() + '/../logs/' + 'quoteVol/' + fileName
        data = CommonFunction().getJsonByFileName(filePath)
        for key in data:
            self.oneDayQuoteVolDict[key] = data[key]
        self.abnormalLogger.info("init24HourQuoteVolDict succ:{}".format(json.dumps(self.oneDayQuoteVolDict)))

    def isAbnormalCurrency(self, currency):
        filePath = os.getcwd() + '/../logs/tradeAbnormal/' + 'AbnormalCurrencyList.log'
        data = CommonFunction().getJsonByFileName(filePath)
        for key in data:
            if currency == key:
                return True
        return False

    #一分钟涨幅超过6%，微信通知
    def hasOver6PercentByOneMinute(self, currency, ohlcvData, beginIndex, endIndex):
        notifyKey = currency + '6Percent'
        if notifyKey in self.notifyByCurHourDict:
            return

        oneMinuteUpPercent = 0.06
        minute1Wusdt = 10000  # 1w usdt
        for index in range(beginIndex, endIndex):
            minuteData = ohlcvData[index]
            # 估算一分钟交易额
            minuteQuoteVol = ((minuteData[OHLCVIndex().highest] + minuteData[OHLCVIndex().lowest]) / 2) * minuteData[OHLCVIndex().volume]
            isOver6Percent = (minuteData[OHLCVIndex().highest] - minuteData[OHLCVIndex().open]) >= (minuteData[OHLCVIndex().open] * oneMinuteUpPercent)

            # 交易额要大于1w usdt
            if isOver6Percent and minuteQuoteVol > minute1Wusdt:
                percent = floor((minuteData[OHLCVIndex().highest] - minuteData[OHLCVIndex().open]) / minuteData[OHLCVIndex().open] * 100)
                logStr = "currency:{}, data:{}, 一分钟涨超:{}%".format(currency, json.dumps(minuteData), percent)
                self.recordDataLogger.info(logStr)
                msgText = "{}, 一分钟涨超6%".format(currency)
                CommonFunction().weiXinNotify(wuchuanruiInfo().token, msgText, "")
                self.notifyByCurHourDict[notifyKey] = 1

    def weixinAbnormalNotify(self, currency, volPercent, minuteData, averOneMinuteVol, notifyKey):
        msgText = "{}, 交易量异常{}".format(currency, volPercent)
        desp = "{},averVol:{},curVol:{},percent:{}".format(currency, floor(averOneMinuteVol), floor(minuteData[OHLCVIndex().volume]), floor(volPercent))
        CommonFunction().weiXinNotify(wuchuanruiInfo().token, msgText, desp)
        self.recordDataLogger.info(desp)

    def hasAbnormalVol(self, currency, ohlcvData, beginIndex, endIndex, averOneMinuteBaseVol, averOneMinuteQuoteVol):
        notifyKey = currency + 'abnormalVol'
        if notifyKey in self.notifyByCurHourDict:
            return

        minute1Wusdt = 10000    #1w usdt
        for index in range(beginIndex, endIndex):
            minuteData = ohlcvData[index]
            volPercent = floor(minuteData[OHLCVIndex().volume] / averOneMinuteBaseVol)
            #计算一分钟涨幅
            upPercent = floor((minuteData[OHLCVIndex().highest] - minuteData[OHLCVIndex().open]) / minuteData[OHLCVIndex().open] * 100)
            #估算一分钟交易额
            minuteQuoteVol = ((minuteData[OHLCVIndex().highest] + minuteData[OHLCVIndex().lowest]) / 2) * minuteData[OHLCVIndex().volume]

            # 在异常币种列表中，交易额超过1w usdt，交易量异常超过50%，涨幅超过2.5%
            isSendNotifyMsg = (self.isAbnormalCurrency(currency) and minuteQuoteVol > minute1Wusdt * 1 and volPercent > 50 and upPercent > 2)
            # 在异常币种列表中，交易额超过3w usdt，交易量异常超过35%
            isSendNotifyMsg = (self.isAbnormalCurrency(currency) and minuteQuoteVol > minute1Wusdt * 3 and volPercent > 35 and upPercent > 1)
            # 在异常币种列表中，交易额超过5w usdt，交易量异常超过20%
            isSendNotifyMsg = (self.isAbnormalCurrency(currency) and minuteQuoteVol > minute1Wusdt * 5 and volPercent > 20 and upPercent > 1)
            # 在异常币种列表中，交易额超过8w usdt，交易量异常超过10%
            isSendNotifyMsg = (self.isAbnormalCurrency(currency) and minuteQuoteVol > minute1Wusdt * 8 and volPercent > 10 and upPercent > 1)

            if isSendNotifyMsg:
                self.weixinAbnormalNotify(currency, volPercent, minuteData, averOneMinuteBaseVol, notifyKey)
                self.notifyByCurHourDict[notifyKey] = 1
                return

    def notifyByTradeAbnormal(self, currency, ohlcvData):
        if len(ohlcvData) == 0:
            return
        beginIndex = len(ohlcvData) - 5 #遍历最新的4条一分钟K线
        endIndex = len(ohlcvData) - 1
        self.hasOver6PercentByOneMinute(currency, ohlcvData, beginIndex, endIndex)

        averOneMinuteBaseVol = self.oneDayBaseVolDict[currency] / (24 * 60)     # 计算平均一分钟交易量
        averOneMinuteQuoteVol = self.oneDayQuoteVolDict[currency] / (24 * 60)   # 计算平均一分钟交易额
        self.hasAbnormalVol(currency, ohlcvData, beginIndex, endIndex, averOneMinuteBaseVol, averOneMinuteQuoteVol)

    def tradeAbnormalByCurrency(self, exchange, listCurrency):
        if self.recordCurDayDict['time'] != TimeInterface().getCurTimeStr('%d'):
            self.notifyByCurHourDict.clear()
            self.recordCurDayDict['time'] = TimeInterface().getCurTimeStr('%d')

        timeFrequency = '1m'
        for currency in listCurrency:
            ohlcvData = ExchangeInterface().getOHLCVDataByCurrency(exchange, currency, timeFrequency)
            self.notifyByTradeAbnormal(currency, ohlcvData)

        loggerStr = "quantTradeAbnormal logger, time:{}".format(TimeInterface().timeStampToShanghaiTime(time.time() * 1000))
        self.abnormalLogger.info(loggerStr)

    def quantTradeAbnormal(self):
        self.abnormalLogger.info("quantTradeAbnormal come in")
        exchange = ExchangeInterface().initOkxExchange()
        listCurrency = ExchangeInterface().getAllCurrencyList(exchange)
        scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
        scheduler.add_job(self.tradeAbnormalByCurrency, 'cron', hour='7-23', minute='*/3', args=[exchange, listCurrency])
        scheduler.add_job(self.init24HourBaseVolDict, 'cron', hour=0, minute=3)   # 记录前一天（24小时）的交易量
        scheduler.add_job(self.init24HourQuoteVolDict, 'cron', hour=0, minute=3)  # 记录前一天（24小时）的交易额
        scheduler.start()

    def test(self):
        self.abnormalLogger.info("quantTradeAbnormal come in")
        exchange = ExchangeInterface().initOkxExchange()
        listCurrency = ExchangeInterface().getAllCurrencyList(exchange)
        self.tradeAbnormal(exchange, listCurrency)

if __name__ == '__main__':
    #QuantTradeAbnormal().test()
    QuantTradeAbnormal().quantTradeAbnormal()
