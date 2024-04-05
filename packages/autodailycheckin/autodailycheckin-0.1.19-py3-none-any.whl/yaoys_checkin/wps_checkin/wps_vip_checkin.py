# encoding=utf8
import json
import os
import time

import requests
from requests.cookies import cookiejar_from_dict

from yaoys_checkin.checkin_util.logutil import log_info
from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.model.all_class_parent import allClassParent

get_vip_header = {
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 WpsOfficeApp/12.1.0.15120 (1)',
    'origin': 'https://vip.wps.cn',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://vip.wps.cn/',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
}
vip_header = {
    'Connection': 'close',
    'content-length': '204',
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.20 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://vip.wps.cn',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://vip.wps.cn/spa/2021/wps-sign/?position=2020_vip_massing&client_pay_version=202301',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
}


class wps_vip(allClassParent):
    def __init__(self, **kwargs):
        super(wps_vip, self).__init__(**kwargs)
        self.session = None
        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])

        self.vip_url = "https://vipapi.wps.cn/wps_clock/v2"
        self.checkin_message, self.is_success = self.wps_vip_sign()

    def __wps_checkin_get_vip__(self):
        if self.cookie is None:
            raise Exception('The cookie is None')
        if self.cookie.startswith("cookie:"):
            self.cookie = self.cookie[len("cookie:"):]
        self.session = requests.sessions.session()
        cookie_dict = {i.split("=")[0]: i.split("=")[1] for i in self.cookie.split("; ")}
        get_resp = self.session.get(url=self.vip_url, cookies=cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True), headers=get_vip_header, timeout=5, verify=False)
        data = {
            'double': '0',
            'v': '12.1.0.15120',
            'p': 'BZqujL7tJMu+REvH+2gNsy+5TF666q6LfPQMWpzMLXRQ26PAHo55PKphN0tmjrZ+gykfxTHRL/THXfNSj8mBwZX5bB66GXcr56thhhcQbysSycNe7FOu3JP599FXHnAmD2PCkBwuJzJIopBiqRu06/+J8Ab9CnlIHwOR5ofMb3I='
        }

        vip_resp = self.session.post(url=self.vip_url, cookies=cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True),
                                     headers=vip_header, timeout=5, data=data, verify=False)
        vip_resp_json = json.loads(vip_resp.text)
        if "UserNotLogin" in vip_resp.text:
            return f'签到失败: Cookie已失效', False
        is_success = True
        if 'result' in vip_resp_json and vip_resp_json['result'] == 'ok':
            checkin_message = f'获取wps会员时长成功，得到名为:{vip_resp_json["data"]["member"]["name"]} 奖励,会员时长为{vip_resp_json["data"]["member"]["hour"]}小时\t'
        elif 'result' in vip_resp_json and vip_resp_json['result'] == 'error':
            checkin_message = '获取会员时长失败，由于Wps签到策略，请手动签到获取会员时长\t'
            is_success = False
        else:
            checkin_message = '获取会员时长异常\t'
            is_success = False
        message = f'签到信息: {checkin_message}'
        return message, is_success

    def wps_vip_main(self):
        # 执行签到
        is_success = True
        if self.cookie is not None and len(self.cookie) > 0:
            account_checkin_message, is_success = self.__wps_checkin_get_vip__()
            # 存在账户签到信息，说明成功执行了签到
            if account_checkin_message is not None and len(account_checkin_message) > 0:
                log_info(f"[Wps_vip_Account_{self.account_index}]:" + str(account_checkin_message), my_logger=self.logger)
                self.checkin_message.append(f"[Wps_vip_Account_{self.account_index}] :" + account_checkin_message + "    \n")
        else:
            is_success = False
            self.checkin_message.append(f"[Wps_vip_Account_{self.account_index}] :cookie is None    \n")
        return self.checkin_message, is_success

    def wps_vip_sign(self):
        if self.checkin_verification is None or self.checkin_verification == '':
            return ''.join(self.checkin_message), False
        try:
            is_success = True
            # 如果是字符串，说明是单个cookie
            if self.checkin_verification is not None and len(self.checkin_verification) > 0:
                log_info('*******************************Wps vip checkin*******************************', my_logger=self.logger)
                if isinstance(self.checkin_verification, str) is True:
                    self.cookie = self.checkin_verification
                    self.account_index = 1
                    self.checkin_message, is_success = self.wps_vip_main()
                elif isinstance(self.checkin_verification, list) is True:
                    for i in range(0, len(self.checkin_verification)):
                        if isinstance(self.checkin_verification[i], dict) is True:
                            self.cookie = self.checkin_verification[i]['cookie']
                            self.account_index = i + 1
                            self.checkin_message, is_success = self.wps_vip_main()
                        else:
                            log_info('Wps vip config error' + '    \n', my_logger=self.logger)
                            self.checkin_message.append('Wps vip config error' + '    \n')
                            is_success = False
                        if self.more_time_sleep > 0:
                            time.sleep(self.more_time_sleep)
                else:
                    log_info('Wps vip config error' + '    \n', my_logger=self.logger)
                    self.checkin_message.append('Wps vip config error' + '    \n')
                    is_success = False
                log_info('*******************************Wps vip checkin complete*******************************', my_logger=self.logger)
                return ''.join(self.checkin_message), is_success
        except Exception as e:
            self.checkin_message.append('main function: Wps vip checkin error, the error is ' + str(e) + '    \n')
            log_info('main function: Wps vip checkin error, the error is ' + str(e) + '    \n', my_logger=self.logger)
            log_info('*******************************Wps vip error*******************************', my_logger=self.logger)
            is_success = False
            return ''.join(self.checkin_message), is_success
