import json

import requests


class CommonFunction:

    def weiXinNotify(self, token, msgText, desp):
        requests.get("http://wx.xtuis.cn/{}.send?text={}&desp={}".format(token, msgText, desp))

    def getJsonByFileName(self, filePath):
        with open(filePath, 'r') as f:
            data = json.load(f)
            return data