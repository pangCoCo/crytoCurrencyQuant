import os
import sys

cwdStr = os.getcwd() + '/../'
sys.path.append(cwdStr)

from quantLogic.OneHourDownNotify import OneHourDownNotify
from quantLogic.QuantTradeAbnormal import QuantTradeAbnormal
from utils.ExchangeUtil import ExchangeInterface
from quantLogic.QuantScheduledTask import initTask

def quantMain():
    initTask()
    exchangeOKX = ExchangeInterface().initOkxExchange()
    exchangeBinance = ExchangeInterface().initBinanceExchange()
    exchangeList = [exchangeOKX, exchangeBinance]
    QuantTradeAbnormalObj = QuantTradeAbnormal()
    OneHourDownNotifyObj = OneHourDownNotify()
    while True:
        #OneHourDownNotifyObj.taskOfOneHourDown(exchangeList)
        QuantTradeAbnormalObj.tradeAbnormal(exchangeList[0])

if __name__ == '__main__':
    quantMain()