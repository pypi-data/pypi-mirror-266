# encoding=utf8
import json
import os
import random
import time

import requests
from requests.cookies import cookiejar_from_dict

from yaoys_checkin.checkin_util.logutil import log_info
from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.model.all_class_parent import allClassParent

cloud_header = {

    'content-length': '10',
    'accept': '*/*',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://zt.wps.cn',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://zt.wps.cn/spa/2019/vip_mobile_sign_v2/?csource=pc_cloud_membercenter&position=pc_cloud_sign',
    'accept-encoding': 'gzip, deflate, br',
}

captcha_header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
}


class wps_cloud(allClassParent):
    def __init__(self, **kwargs):
        super(wps_cloud, self).__init__(**kwargs)
        self.session = None
        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])

        self.cloud_url = "https://vip.wps.cn/sign/v2"
        self.captcha_url = f"https://vip.wps.cn/checkcode/signin/captcha.png?platform=8&encode=0&img_witdh=336&img_height=84.48&v={str(round(time.time() * 1000))}"
        self.data = {
            'platform': '8'
        }
        self.captcha_data = {
            'platform': '8',
            "captcha_pos": "217.0125,36.0125|278.0125,25.0125",
            "img_witdh": "336",
            "img_height": "84.48"
        }
        self.need_captcha = False
        self.cookie_dict = None
        self.checkin_message, self.is_success = self.wps_cloud_sign()

    def __get_captcha__(self):
        self.session.get(url=self.captcha_url, headers=captcha_header,
                         cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True), timeout=5, verify=False)

    def __cloud_sign__(self):
        # 如果需要验证码，则使用验证码的data
        if self.need_captcha is True:
            data = self.captcha_data
        else:
            # 不需要验证码，则使用普通的data
            data = self.data

        cloud_resp = self.session.post(url=self.cloud_url, cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True),
                                       headers=cloud_header, timeout=5, data=data, verify=False)
        cloud_resp_json = json.loads(cloud_resp.text)

        is_success = True
        # 状态类型，0：成功，1：需要验证码，2：验证码过期，3：已经签到过，重复签到，4：未知异常
        code = 0
        # '{"result":"error","data":"","msg":"no_login"}'
        if "no_login" in cloud_resp.text:
            return f'签到失败: Cookie已失效', False, -1

        if 'result' in cloud_resp_json and cloud_resp_json['result'] == 'ok':
            checkin_message = f'签到成功，已成功获取云空间\t'

        elif 'result' in cloud_resp_json and cloud_resp_json['result'] == 'error':
            if cloud_resp_json["msg"] == 'need_captcha':
                checkin_message = f'签到失败，此次签到需要验证码,请手动签到\t'
                is_success = False
                code = 1
            # 'captcha_expired'
            elif cloud_resp_json["msg"] == 'captcha_expired':
                checkin_message = f'签到失败，验证码已过期\t'
                is_success = False
                code = 2
            elif cloud_resp_json["msg"] == '10003':
                checkin_message = f'签到失败，已经签到过，请不要重复签到\t'
                is_success = False
                code = 3
            else:
                checkin_message = f'签到失败，请手动签到\t'
                is_success = False
                code = 4
        else:
            checkin_message = '获取cloud 云空间异常\t'
            is_success = False
            code = 4
        message = f'签到信息: {checkin_message}'
        return message, is_success, code

    def __wps_checkin_get_cloud__(self):
        if self.cookie is None:
            raise Exception('The cookie is None')
        if self.cookie.startswith("cookie:"):
            self.cookie = self.cookie[len("cookie:"):]
        self.session = requests.sessions.session()
        self.cookie_dict = {i.split("=")[0]: i.split("=")[1] for i in self.cookie.split("; ")}
        # 尝试不使用验证码签到
        checkin_message, is_success, code = self.__cloud_sign__()
        # 签到成功
        if is_success is True and code == 0:
            return checkin_message, is_success
        # 签到失败，需要验证码或者验证码已失效
        elif (is_success is False and code == 1) or (is_success is False and code == 2):
            # 休眠3秒
            time.sleep(self.time_sleep)
            # 调用获取验证码
            self.__get_captcha__()
            # 设置需要验证码
            self.need_captcha = True
            # 休眠3秒
            time.sleep(self.time_sleep)
            checkin_message, is_success, code = self.__cloud_sign__()
            checkin_message = '尝试饶过验证码实现签到,' + checkin_message
            return checkin_message, is_success
        else:
            return checkin_message, is_success

    def wps_cloud_main(self):
        is_success = True
        # 执行签到
        if self.cookie is not None and len(self.cookie) > 0:
            account_checkin_message, is_success = self.__wps_checkin_get_cloud__()
            # 存在账户签到信息，说明成功执行了签到
            if account_checkin_message is not None and len(account_checkin_message) > 0:
                log_info(f"[Wps_cloud_Account_{self.account_index}]:" + str(account_checkin_message), my_logger=self.logger)
                self.checkin_message.append(f"[Wps_cloud_Account_{self.account_index}] :" + account_checkin_message + "    \n")

        return self.checkin_message, is_success

    def wps_cloud_sign(self):
        if self.checkin_verification is None or self.checkin_verification == '':
            return ''.join(self.checkin_message), False
        try:
            is_success = True
            # 如果是字符串，说明是单个cookie
            if self.checkin_verification is not None and len(self.checkin_verification) > 0:
                log_info('*******************************Wps cloud checkin*******************************', my_logger=self.logger)
                if isinstance(self.checkin_verification, str) is True:
                    self.cookie = self.checkin_verification
                    self.account_index = 1
                    self.checkin_message, is_success = self.wps_cloud_main()
                elif isinstance(self.checkin_verification, list) is True:
                    for i in range(0, len(self.checkin_verification)):
                        if isinstance(self.checkin_verification[i], dict) is True:
                            self.cookie = self.checkin_verification[i]['cookie']
                            self.account_index = i + 1
                            self.checkin_message, is_success = self.wps_cloud_main()
                        else:
                            log_info('Wps cloud config error' + '    \n', my_logger=self.logger)
                            self.checkin_message.append('Wps vip config error' + '    \n')
                            is_success = False
                        if self.more_time_sleep > 0:
                            time.sleep(self.more_time_sleep)
                else:
                    is_success = False
                    log_info('Wps cloud config error' + '    \n', my_logger=self.logger)
                    self.checkin_message.append('Wps cloud config error' + '    \n')
                log_info('*******************************Wps cloud checkin complete*******************************', my_logger=self.logger)
                return ''.join(self.checkin_message), is_success
        except Exception as e:
            self.checkin_message.append('main function: Wps cloud checkin error, the error is ' + str(e) + '    \n')
            log_info('main function: Wps cloud checkin error, the error is ' + str(e) + '    \n', my_logger=self.logger)
            log_info('*******************************Wps cloud error*******************************', my_logger=self.logger)
            is_success = False
            return ''.join(self.checkin_message), is_success
