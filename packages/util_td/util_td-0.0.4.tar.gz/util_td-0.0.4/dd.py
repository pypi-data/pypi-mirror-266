import time
import hmac
import hashlib
import base64
import urllib.parse
import urllib.request
import datetime
import json
import multitasking

class DD():
    def __init__(self, secret, token):
        self.secret = secret
        self.token = token
        self.url = f'https://oapi.dingtalk.com/robot/send?access_token={token}'

    def send_request(self, url, datas):
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }
        sendData = json.dumps(datas)
        sendDatas = sendData.encode("utf-8")
        request = urllib.request.Request(url=url, data=sendDatas, headers=header)
        opener = urllib.request.urlopen(request)
        # # 输出响应结果
        # print(opener.read())

    @multitasking.task
    def send(self, text='Hello DD', title='推送消息', at_all=False):
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        url = self.url + f'&sign={sign}&timestamp={timestamp}'
        # isAtAll：是否@所有人，建议非必要别选，不然测试的时候很尴尬
        dict = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            },
            "at": {
                "isAtAll": False
            }
        }
        self.send_request(url, dict)


