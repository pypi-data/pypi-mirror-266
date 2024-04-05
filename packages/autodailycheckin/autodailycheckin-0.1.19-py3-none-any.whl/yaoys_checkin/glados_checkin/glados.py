# encoding=utf8
import json
import os
import re
import time
from concurrent.futures import ALL_COMPLETED, FIRST_EXCEPTION, ThreadPoolExecutor, as_completed, wait

import requests
from requests.cookies import cookiejar_from_dict

from yaoys_checkin.checkin_util import constants
from yaoys_checkin.checkin_util.logutil import log_info
from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.model.all_class_parent import allClassParent

token_js_header = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'max-age=0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188'
}
sign_header = {
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'content-length': '26',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://glados.rocks',
    'sec-ch-ua': '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'Windows',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35'
}

status_header = {
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'content-length': '26',
    'content-type': 'application/json;charset=UTF-8',
    'sec-ch-ua': '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'Windows',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35'
}


class glados(allClassParent):
    def __init__(self, **kwargs):
        super(glados, self).__init__(**kwargs)
        self.session = None
        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])

        self.base_url = 'https://glados.rocks'
        self.token_js = self.base_url + "/static/js/main~189dec1b.73bf982f.chunk.js"
        self.checkin_document = self.base_url + '/console/checkin'
        self.checkin_url = self.base_url + "/api/user/checkin"
        self.status_url = self.base_url + "/api/user/status"
        self.balance_url = self.base_url + "/api/user/balance"
        self.cookie_dict = None
        self.token = constants.glados_token
        self.token_error_message = 'token error'
        self.cookie_isvalid = 'cookie失效'
        self.repeat_checkin = 'Please Try Tomorrow'
        self.checkin_lucky = 'Checkin! Get 0 day'
        self.free_user_checkin = 'Free users can not checkin anymore'
        if 'retry_checkin_count' in self.config_file['cookieOrUser']['glados']:
            self.retry_checkin_count = int(self.config_file['cookieOrUser']['glados']['retry_checkin_count'])
        else:
            self.retry_checkin_count1 = 10

        self.checkin_count = 0
        self.checkin_message, self.is_success = self.glados_sign()

    def checkin(self):
        data = {"token": self.token}
        checkin_resp = self.session.post(url=self.checkin_url, cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True),
                                         headers=sign_header, timeout=20, json=data)
        checkin_resp_json = json.loads(checkin_resp.text)
        # {'code': 1, 'message': 'oops, token error'}
        if "code" in checkin_resp_json:
            checkin_code = checkin_resp_json["code"]
        else:
            checkin_code = -100
        # token已失效
        if checkin_code == 1 and self.token_error_message in checkin_resp_json["message"]:
            return self.token_error_message, checkin_code, checkin_resp.status_code
        if checkin_code == -2:
            return self.cookie_isvalid, checkin_code, checkin_resp.status_code
        if "message" in checkin_resp_json:
            checkin_message = checkin_resp_json["message"]
        else:
            checkin_message = '签到出现异常，请联系管理员'
        if self.repeat_checkin in checkin_message:
            checkin_message = self.repeat_checkin

        return checkin_message, checkin_code, checkin_resp.status_code

    # 发送请求获取token
    def get_token_by_js(self, url=None):
        js_document = requests.get(url=self.base_url + url, headers=token_js_header)
        token = re.findall(r'("/user/checkin",{token:"(.*?)"})', js_document.text)
        if len(token) > 0 and token is not None:
            self.token = token[0][1]
            constants.glados_token = self.token
            return self.token
        else:
            return None

    # 从签到页面所有js中获取token
    def get_checkin_js(self):
        checkin_docment = self.session.get(url=self.checkin_document,
                                           headers=token_js_header,
                                           cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True),
                                           timeout=20)
        s = re.findall(r'<script src="(.*?)"></script>', checkin_docment.text)

        for i in reversed(s):
            # 从js中获取token
            result = self.get_token_by_js(url=i)
            if result is not None:
                return True

    def __glados_checkin_without_driver__(self):
        if self.cookie is None:
            raise Exception('The cookie is None')
        if self.cookie.startswith("cookie:"):
            self.cookie = self.cookie[len("cookie:"):]
        self.session = requests.sessions.session()
        self.cookie_dict = {i.split("=")[0]: i.split("=")[1] for i in self.cookie.split("; ")}
        # 执行签到
        checkin_message, code, status_code = self.checkin()

        is_lucky_checkin = False
        # 如果是概率签到成功，则重试默认10次
        if self.checkin_lucky in checkin_message:
            while self.checkin_count <= self.retry_checkin_count:
                checkin_message, code, status_code = self.checkin()
                if "Get 1 Day" in checkin_message:
                    is_lucky_checkin = True
                    break
                else:
                    self.checkin_count = self.checkin_count + 1
                time.sleep(1)

        if status_code != 200:
            return f'网络异常，返回的状态码不是200', False
        # token已经失效，根据页面获取所有的js，并解析token
        if code == 1 and checkin_message == self.token_error_message:
            # 从js中更新token
            time.sleep(self.time_sleep)
            self.get_checkin_js()
            # 再次执行签到
            checkin_message, code, status_code = self.checkin()
            #     如果token还是错误
            if code == 1 and checkin_message == self.token_error_message:
                return f'系统异常，token错误', False
            if status_code != 200:
                return f'网络异常，返回的状态码不是200', False

            # 如果是概率签到成功，则重试默认10次
            if self.checkin_lucky in checkin_message:
                while self.checkin_count <= self.retry_checkin_count:
                    checkin_message, code, status_code = self.checkin()
                    if "Get 1 Day" in checkin_message:
                        is_lucky_checkin = True
                        break

                    self.checkin_count = self.checkin_count + 1
                    time.sleep(1)

        # cookie 失效
        if code == -2 and checkin_message == self.cookie_isvalid:
            return f'签到信息: cookie 失效，请更新cookie', False

        # 获取用户天数
        status_resp = self.session.get(self.status_url,
                                       cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True),
                                       headers=status_header,
                                       timeout=20,
                                       json={"token": self.token})
        if status_resp.status_code != 200:
            return f'签到信息: {checkin_message}, 账户剩余天数: 获取失败', False

        if "data" not in status_resp.text or "leftDays" not in status_resp.text:
            return f'签到信息: {checkin_message}, 账户剩余天数: 获取失败', False

        status_resp_json = json.loads(status_resp.text)
        status_message = status_resp_json["data"]
        left_days = int(float(status_message["leftDays"]))

        # 获取会员天数变化记录
        balance = self.session.get(self.balance_url,
                                   cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True),
                                   headers=sign_header,
                                   timeout=20,
                                   json={"token": self.token})

        # 签到类型：points:活动点数签到，ss-1：签到天数
        asset = ""
        # 签到信息
        business = ""
        # 活动点数/天数变化
        change = ""
        # 总天数/总活动点数
        balance_total = ""
        if balance.status_code == 200:
            balance_json = json.loads(balance.text)
            if 'data' in balance_json:
                business = balance_json['data'][0]['business']
                change = balance_json['data'][0]['change']
                asset = balance_json['data'][0]['asset']
                balance_total = balance_json['data'][0]['balance']

        if is_lucky_checkin is True:
            message = '概率签到成功,'
        else:
            message = ''

        if self.free_user_checkin == checkin_message:
            checkin_message = '免费用户无法进行签到，请开通会员'

        if asset == '':
            message += f' {checkin_message}, 账户剩余天数: {left_days}'
        elif asset == "points":
            message += f' {checkin_message}, 账户剩余天数: {left_days}, 签到日志: {business},活动点数变化: {change} 现有活动点数: {balance_total} points'
        elif asset == "ss-1":
            message += f' {checkin_message}, 账户剩余天数: {left_days}, 签到日志: {business},天数变化: {change} 剩余天数: {balance_total} 天'
        else:
            message += f' {checkin_message}, 账户剩余天数: {left_days}, 签到日志: 未知类型'
        return message, True

    def glados_main(self):
        # gloads 执行签到
        status = False
        if self.cookie is not None and len(self.cookie) > 0:
            self.checkin_count = 0
            account_checkin_message, status = self.__glados_checkin_without_driver__()
            # 存在账户签到信息，说明成功执行了签到
            if account_checkin_message is not None and len(account_checkin_message) > 0:
                log_info(f"[Glados账号_{self.account_index}]:" + str(account_checkin_message), my_logger=self.logger)
                self.checkin_message.append(f"[Glados账号_{self.account_index}] :" + account_checkin_message + "    \n")

        return self.checkin_message, status

    def glados_sign(self):
        if self.checkin_verification is None or self.checkin_verification == '':
            return ''.join(self.checkin_message), False
        try:
            status = False
            # 如果是字符串，说明是单个cookie
            if self.checkin_verification is not None and len(self.checkin_verification) > 0:
                log_info('*******************************glados checkin*******************************', my_logger=self.logger)
                if isinstance(self.checkin_verification, str) is True:
                    self.cookie = self.checkin_verification
                    self.account_index = 1
                    self.checkin_message, status = self.glados_main()
                elif isinstance(self.checkin_verification, list) is True:
                    for i in range(0, len(self.checkin_verification)):
                        if isinstance(self.checkin_verification[i], dict) is True:
                            self.cookie = self.checkin_verification[i]['cookie']
                            self.account_index = i + 1
                            self.checkin_message, status = self.glados_main()
                        else:
                            log_info('glados config error' + '    \n', my_logger=self.logger)
                            self.checkin_message.append('glados config error' + '    \n')
                            status = False
                        if self.more_time_sleep > 0:
                            time.sleep(self.more_time_sleep)
                else:
                    log_info('glados config error' + '    \n', my_logger=self.logger)
                    self.checkin_message.append('glados config error' + '    \n')
                    status = False
                log_info('*******************************glados checkin complete*******************************', my_logger=self.logger)
                return ''.join(self.checkin_message), status
        except Exception as e:
            self.checkin_message.append('main function: gloads checkin error, the error is ' + str(e) + '    \n')
            log_info('main function: gloads checkin error, the error is ' + str(e) + '    \n', my_logger=self.logger)
            log_info('*******************************glados error*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), False
