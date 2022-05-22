import logging
import os

class Log:

    def __init__(self, file_name, outputFormat=None, dirName=None):
        if "/" not in dirName:
            dirName += '/'
        if outputFormat is None or outputFormat == "":
            outputFormat = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"  # 设置输出格式

        if dirName is None:
            dirName = ''
        self.initLog(file_name, outputFormat, dirName)

    def initLog(self, file_name, outputFormat, dirName):
        # 第一步，创建一个logger
        self.logger = logging.getLogger(file_name)  # file_name为多个logger的区分唯一性
        self.logger.setLevel(logging.DEBUG)  # Log等级总开关

        # 第二步，创建handler，用于写入日志文件和屏幕输出
        logPath = os.getcwd() + '/../logs/' + dirName
        if not os.path.isdir(logPath):
            os.makedirs(logPath)  # 创建文件夹
        logfile = logPath + file_name + '.log'
        formatter = logging.Formatter(outputFormat)
        if os.path.exists(logfile) == False:  # 判断文件是否存在，不存在就创建
            open(logfile, 'w', encoding="utf-8")

        # 文件输出
        mode = 'a'  # 追加写
        fh = logging.FileHandler(logfile, mode=mode)
        fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
        fh.setFormatter(formatter)
        # 先清空handler, 再添加
        self.logger.handlers = []
        self.logger.addHandler(fh)

    def info(self, message):
        self.logger.info(message)