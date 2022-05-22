import datetime
import pytz
import time

class TimeInterface:

    """
    :param: timeStamp 毫秒级时间戳
    :return: 将美国服务器时间戳转换成上海时间
    """
    def timeStampToShanghaiTime(self, timeStamp, format='%Y-%m-%d %H:%M:%S'):
        timeStamp = float(timeStamp / 1000)
        shanghaiTime = datetime.datetime.fromtimestamp(int(timeStamp), pytz.timezone('Asia/Shanghai')).strftime(format)
        return shanghaiTime

    """
    :param: timeStamp 毫秒级时间戳
    :return: 获取前几天或者是后几天的时间
    """
    def getOffsetDayStr(self, timeStamp, offset, format='%Y-%m-%d'):
        shanghaiTime = self.getOffsetDayTime(timeStamp, offset)
        return shanghaiTime.strftime(format)

    def getOffsetDayTime(self, timeStamp, offset):
        timeStamp = float(timeStamp / 1000)
        shanghaiTime = datetime.datetime.fromtimestamp(int(timeStamp), pytz.timezone('Asia/Shanghai'))
        shanghaiTime = shanghaiTime + datetime.timedelta(days=offset)
        return shanghaiTime

    """
    :return: 获取当前小时数，例如：22,23
    """
    def getCurTimeStr(self, format='%H'):
        timeStamp = time.time()
        return datetime.datetime.fromtimestamp(int(timeStamp), pytz.timezone('Asia/Shanghai')).strftime(format)

    """
    :return: 获取minuteNum分钟的秒数
    """
    def getMinuteSecondNum(minuteNum):
        oneMinute = 60
        return oneMinute * minuteNum