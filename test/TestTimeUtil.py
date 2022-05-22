from utils.TimeUtil import TimeInterface

import time

def testTimeUtils():
    timeStamp = time.time() * 1000
    result = TimeInterface().getOffsetDayStr(timeStamp, 1)
    print("result:", result)        #2022-04-02

if __name__ == '__main__':
    testTimeUtils()