import os
import psutil
from apscheduler.schedulers.background import BackgroundScheduler

from utils.QuantLogging import Log

oneHourDownLogger = Log('monitorQuant')

""" 
get process by name
return the first process if there are more than one
"""
def getProcByName(pname):
    for proc in psutil.process_iter():
        try:
            # return if found one
            procList = psutil.Process(proc.pid).cmdline()
            procStr = ''
            for str in procList:
                procStr += str + ' '
            if procStr.lower().find(pname.lower()) != -1:
                return proc
        except psutil.AccessDenied:
            pass
        except psutil.NoSuchProcess:
            pass

    oneHourDownLogger.info("process:{} is none".format(pname))
    return None

def monitorQuant(commad, pname='python3 -i OneHourDownNotify.py'):
    try:
        process = getProcByName(pname)
        if not (process is None):
            return
        else:
            os.system(commad)
    except Exception as e:
        print(Exception, "monitorQuant:", e)
        oneHourDownLogger.info("monitorQuant exception")

def monitorQuantTask(commad):
    scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(monitorQuant, 'interval', minutes=15, args=[commad])
    scheduler.start()

if __name__ == '__main__':
    commad = 'python3 -i OneHourDownNotify.py'
    monitorQuantTask(commad)