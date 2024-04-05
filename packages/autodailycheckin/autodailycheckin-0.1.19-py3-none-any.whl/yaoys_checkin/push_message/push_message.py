import json
import os

import requests

from yaoys_checkin.checkin_util.constants import request_timeout
from yaoys_checkin.checkin_util.logutil import log_info
from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger

push_message_logger, log_config = get_checkin_logger(config_file=None, log_name=str(os.path.basename(__file__)).split('.')[0])


class pushPlus(object):
    def __init__(self, token=None, checkin_message=None, logger=None, title=None):
        self.token = token
        self.checkin_message = checkin_message
        self.logger = logger
        self.title = title
        if self.logger is None:
            self.logger = push_message_logger

    def send_message(self):
        if self.token is None or str(self.token) == '':
            return None
        else:
            if self.checkin_message is None:
                self.checkin_message = ''
            content = ''
            for i in range(0, len(self.checkin_message)):
                content += str(self.checkin_message[i])
            # content = '\n'.join(str(i) for i in self.checkin_message)
            payload = {'token': self.token, "channel": "wechat", "template": "html", "content": content, "title": self.title}
            resp = requests.post("https://www.pushplus.plus/send", params=payload, timeout=request_timeout, verify=False)
            resp_json = json.loads(resp.text)
            if resp.status_code == 200:
                log_info('push plus success message:' + str(resp_json['msg']), my_logger=self.logger)
            else:
                log_info('push message to push plus error,the message is:' + str(resp_json['msg']), my_logger=self.logger)
            resp.close()
            return str(resp_json['msg'])


class server(object):
    def __init__(self, token=None, checkin_message=None, logger=None, title=None):
        self.token = token
        self.checkin_message = checkin_message
        self.logger = logger
        self.title = title
        if self.logger is None:
            self.logger = push_message_logger

    def send_message(self):

        if self.checkin_message is None:
            self.checkin_message = ''
        content = ''
        for i in range(0, len(self.checkin_message)):
            content += str(self.checkin_message[i])
        payload = {"title": self.title, "desp": content}
        resp = requests.post(f"https://sctapi.ftqq.com/{self.token}.send", params=payload, timeout=request_timeout, verify=False)
        result = resp.json()

        if result["code"] == 0:
            log_info("Push the message to server success(code:0),the code is:" + str(result["code"]), my_logger=self.logger)
        if result["code"] != 0:
            log_info("Push the message to server error(code!=0),The error message is " + str(result["code"]) + str(result["message"]), my_logger=self.logger)
        resp.close()
        return str(result["message"])
