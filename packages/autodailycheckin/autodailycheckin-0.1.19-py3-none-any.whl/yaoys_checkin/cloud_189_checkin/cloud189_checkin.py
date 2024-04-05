# -*- coding: utf-8 -*-
# @FileName  :checkin-1.py
# @Time      :2023/3/26 15:37
# @Author    :yaoys
# @Desc      : 代码源地址：https://github.com/wd210010/only_for_happly/blob/main/tyyun.py,对代码错误进行修改，并增加了多账号签到
import base64
import hashlib
import os
import re
import time

import requests
import rsa

from yaoys_checkin.checkin_util.logutil import log_info
from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.model.all_class_parent import allClassParent

BI_RM = list("0123456789abcdefghijklmnopqrstuvwxyz")


def int2char(a):
    return BI_RM[a]


b64map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def b64tohex(a):
    d = ""
    e = 0
    c = 0
    for i in range(len(a)):
        if list(a)[i] != "=":
            v = b64map.index(list(a)[i])
            if 0 == e:
                e = 1
                d += int2char(v >> 2)
                c = 3 & v
            elif 1 == e:
                e = 2
                d += int2char(c << 2 | v >> 4)
                c = 15 & v
            elif 2 == e:
                e = 3
                d += int2char(c)
                d += int2char(v >> 2)
                c = 3 & v
            else:
                e = 0
                d += int2char(c << 2 | v >> 4)
                d += int2char(15 & v)
    if e == 1:
        d += int2char(c << 2)
    return d


def rsa_encode(j_rsakey, string):
    rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC KEY-----"
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
    result = b64tohex(
        (base64.b64encode(rsa.encrypt(f'{string}'.encode(), pubkey))).decode())
    return result


def calculate_md5_sign(params):
    return hashlib.md5('&'.join(sorted(params.split('&'))).encode('utf-8')).hexdigest()


class cloud189(allClassParent):

    def __init__(self, **kwargs):
        super(cloud189, self).__init__(**kwargs)
        self.session = None
        self.login_message = None
        if self.checkin_message is None:
            self.checkin_message = []
        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq '
                          'proVersion/1.0.6',
            "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
            "Host": "m.cloud.189.cn",
            "Accept-Encoding": "gzip, deflate",
        }
        self.checkin_message, self.is_success = self.cloud189_sign()

        # self.get_checkin_message()

    def check_args(self):
        if self.phone is None or len(str(self.phone)) <= 0:
            self.judge_args = False
        if self.password is None or len(str(self.password)) <= 0:
            self.judge_args = False
        return self.judge_args

    def cloud189_checkin(self):
        if self.phone is None or len(self.phone) <= 0 or self.password is None or len(self.password) <= 0:
            return self.checkin_message
        message = '[cloud189_account_{}] : '.format(self.account_index)
        self.session = requests.sessions.session()
        signStr, cj1Str, cj2Str, cj3Str = '', '', '', ''

        is_login = self.login()

        if is_login is False:
            message += ' login error, message is {} '.format(self.login_message)
            signStr, cj1Str, cj2Str, cj3Str = '', '', '', ''
        else:
            signStr, cj1Str, cj2Str, cj3Str = self.checkin()
            message += signStr + ',' + cj1Str + ',' + cj2Str + ',' + cj3Str + '\n'
        log_info('[account_{} cloud189] message: {},{},{},{},{} \n'.format(self.account_index, self.login_message, signStr, cj1Str, cj2Str, cj3Str), my_logger=self.logger)

        return message

    def checkin(self):
        # 签到链接
        surl = f'https://api.cloud.189.cn/mkt/userSign.action?rand={str(round(time.time() * 1000))}&clientType=TELEANDROID&version=8.6.3&model=SM-G930K'
        response = self.session.get(surl, headers=self.headers, timeout=10)
        netdiskBonus = response.json()['netdiskBonus']
        if response.json()['isSign'] == "false":
            signStr = f"未签到，获得{netdiskBonus}M空间"
        else:
            signStr = f"已签到，获得{netdiskBonus}M空间"
        time.sleep(self.time_sleep)

        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq '
        #                   'proVersion/1.0.6',
        #     "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
        #     "Host": "m.cloud.189.cn",
        #     "Accept-Encoding": "gzip, deflate",
        # }
        # 抽奖1
        url = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN&rand={str(round(time.time() * 1000))}'
        response = self.session.get(url, headers=self.headers, timeout=10)
        cjStr1 = ''
        if "errorCode" in response.text:
            cjStr1 = f"抽奖1: {response.json()['errorCode']} "
        else:
            if "prizeName" in response.text:
                description = response.json()["prizeName"]
                cjStr1 = f"抽奖1: 抽奖获得{description} "
        time.sleep(self.time_sleep)

        # 抽奖2
        url2 = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN_PHOTOS&activityId=ACT_SIGNIN&rand={str(round(time.time() * 1000))}'
        response = self.session.get(url2, headers=self.headers, timeout=10)
        cjStr2 = ''
        if "errorCode" in response.text:
            cjStr2 = f"抽奖2: {response.json()['errorCode']} "
        else:
            if "prizeName" in response.text:
                description = response.json()["prizeName"]
                cjStr2 = f"抽奖2: 抽奖获得{description} "
        time.sleep(self.time_sleep)

        # phone_header = {
        #     'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Ecloud/9.2.8 iOS/16.6 clientId/83F8F3AA-8B76-4CAE-BB93-FE2A921D49D0 clientModel/iPhone proVersion/1.0.5',
        #     "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?from=shakeLottery",
        #     "Host": "m.cloud.189.cn",
        #     "Accept-Encoding": "gzip, deflate",
        # }
        # 抽奖3  0.5534584101612121
        url3 = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_2022_FLDFS_KJ&activityId=ACT_SIGNIN&noCache={str(round(time.time() * 1000))}'
        cjStr3 = '手机抽奖获取空间错误'
        response = self.session.get(url3, headers=self.headers, timeout=10)
        if "errorCode" in response.text:
            cjStr3 = f"抽奖3: {response.json()['errorCode']} "
        else:
            if "prizeName" in response.text:
                description = response.json()["prizeName"]
                cjStr3 = f"抽奖3: 抽奖获得{description} "
        return signStr, cjStr1, cjStr2, cjStr3

    def login(self):
        # self.session = requests.sessions.session()
        # https://m.cloud.189.cn/login2014.jsp?redirectURL=https://m.cloud.189.cn/zhuanti/2021/shakeLottery/index.html
        url = ""
        urlToken = "https://m.cloud.189.cn/udb/udb_login.jsp?pageId=1&pageKey=default&clientType=wap&redirectURL=https://m.cloud.189.cn/zhuanti/2021/shakeLottery/index.html"

        r = self.session.get(urlToken)
        pattern = r"https?://[^\s'\"]+"  # 匹配以http或https开头的url
        match = re.search(pattern, r.text)  # 在文本中搜索匹配
        if match:  # 如果找到匹配
            url = match.group()  # 获取匹配的字符串
            # print(url)  # 打印url
        else:  # 如果没有找到匹配
            self.login_message = "没有找到url"
            return False
        time.sleep(self.time_sleep)
        r = self.session.get(url)
        # print(r.text)
        pattern = r"<a id=\"j-tab-login-link\"[^>]*href=\"([^\"]+)\""  # 匹配id为j-tab-login-link的a标签，并捕获href引号内的内容
        match = re.search(pattern, r.text)  # 在文本中搜索匹配
        if match:  # 如果找到匹配
            href = match.group(1)  # 获取捕获的内容
            # print("href:" + href)  # 打印href链接
        else:  # 如果没有找到匹配
            self.login_message = "没有找到href链接"
            return False
        time.sleep(self.time_sleep)
        r = self.session.get(href)
        captchaToken = re.findall(r"captchaToken' value='(.+?)'", r.text)[0]
        lt = re.findall(r'lt = "(.+?)"', r.text)[0]
        returnUrl = re.findall(r"returnUrl= '(.+?)'", r.text)[0]
        paramId = re.findall(r'paramId = "(.+?)"', r.text)[0]
        j_rsakey = re.findall(r'j_rsaKey" value="(\S+)"', r.text, re.M)[0]
        self.session.headers.update({"lt": lt})

        username = rsa_encode(j_rsakey, self.phone)
        password = rsa_encode(j_rsakey, self.password)
        url = "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/76.0',
            'Referer': 'https://open.e.189.cn/',
        }
        data = {
            "appKey": "cloud",
            "accountType": '01',
            "userName": f"{{RSA}}{username}",
            "password": f"{{RSA}}{password}",
            "validateCode": "",
            "captchaToken": captchaToken,
            "returnUrl": returnUrl,
            "mailSuffix": "@189.cn",
            "paramId": paramId
        }
        time.sleep(self.time_sleep)
        r = self.session.post(url, data=data, headers=headers, timeout=5)
        if 'result' not in r.text and 'msg' not in r.text:
            return False
        is_login = False
        self.login_message = r.json()['msg']
        if r.json()['result'] == 0 and '登录成功' in self.login_message:
            is_login = True
            redirect_url = r.json()['toUrl']
            self.session.get(redirect_url)
        return is_login

    def cloud189_sign(self):
        if self.checkin_verification is None or self.checkin_verification == '':
            return ''.join(self.checkin_message), False
        try:
            # 天翼云盘执行签到
            # 单账号签到
            message = ''
            log_info('*******************************cloud189 checkin*******************************', my_logger=self.logger)
            if isinstance(self.checkin_verification, dict) is True:
                self.phone = self.checkin_verification['phone']
                self.password = self.checkin_verification['password']
                if self.check_args() is False:
                    return ''.join(self.checkin_message), False
                self.account_index = 1
                message = self.cloud189_checkin()
                self.checkin_message.append(message)
            # 多账号签到
            elif isinstance(self.checkin_verification, list) is True:
                for i in range(0, len(self.checkin_verification)):
                    if isinstance(self.checkin_verification[i], dict) is True:
                        self.phone = self.checkin_verification[i]['phone']
                        self.password = self.checkin_verification[i]['password']
                        if self.check_args() is False:
                            return ''.join(self.checkin_message), False
                        self.account_index = i + 1
                        message = self.cloud189_checkin()
                    else:
                        log_info('cloud189 config error' + '    \n', my_logger=self.logger)
                        message += 'cloud189 config error' + '    \n'
                    self.checkin_message.append(message)

                    if self.more_time_sleep > 0:
                        time.sleep(self.more_time_sleep)
            else:
                log_info('cloud189 config error' + '    \n', my_logger=self.logger)
                message += 'cloud189 config error' + '    \n'
            log_info('*******************************cloud189 checkin complete*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), True
        except Exception as e:
            self.checkin_message.append('main function: cloud189 checkin error, the error is ' + str(e) + '    \n')
            log_info('main function: cloud189 checkin error, the error is ' + str(e) + '    \n', my_logger=self.logger)
            log_info('*******************************cloud189 error*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), False
