# -*- coding: utf-8 -*-
# @FileName  :ableSci_checkin.py
# @Time      :2022/8/20 8:19
# @Author    :yaoys
# @Desc      :
import json
import os
import time

import requests
from requests.cookies import cookiejar_from_dict

from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.checkin_util.logutil import log_info
from yaoys_checkin.model.all_class_parent import allClassParent

checkin_header = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'x-requested-with': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': "Windows",
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.ablesci.com/',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'pragma': 'no-cache'
}


class ableSci(allClassParent):

    def __init__(self, **kwargs):
        super(ableSci, self).__init__(**kwargs)

        self.session = None
        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])

        self.checkin_message, self.is_success = self.able_sci_sign()

    def __able_sci_checkin_withoutDriver__(self):
        if self.cookie is None:
            raise Exception('The cookie is None')
        if self.cookie.startswith("cookie:"):
            self.cookie = self.cookie[len("cookie:"):]
        self.session = requests.sessions.session()
        cookie_dict = {i.split("=")[0]: i.split("=")[1] for i in self.cookie.split("; ")}
        resp = self.session.get('https://www.ablesci.com/user/sign', cookies=cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True), headers=checkin_header)
        if resp.status_code != 200:
            return '签到失败，发生未知错误', False
        resp_json = json.loads(resp.text)
        # Cookie失效信息
        # {'code': 1, 'msg': '<div class="need-login-tips">对不起，您的操作需要登录才可以进行。<br><a class="able-link" href="/site/login">点击登录/注册 <i class="layui-icon layui-icon-link"></i></a></div>'}
        # 重复签到信息
        # '{"code":1,"msg":"\\u7b7e\\u5230\\u5931\\u8d25\\uff0c\\u60a8\\u4eca\\u5929\\u5df2\\u4e8e [07:20:07] \\u7b7e\\u5230\\u3002"}'
        if 'code' not in resp.text or 'msg' not in resp.text:
            return '签到响应错误，请联系开发者', False
        if resp_json['code'] == 1:
            if '登录' in resp_json['msg']:
                return 'Cookie已失效,请更新Cookie', False
            return resp_json['msg'], True
        # ablesci-serial=e57a0a2dd0cf326fbaf4bd1684bbc5b6;

        if 'data' not in resp.text or 'signcount' not in resp.text or 'signpoint' not in resp.text:
            return '签到响应错误，请联系开发者', False

        signcount = 0
        signpoint = 0
        msg = resp_json['msg']
        if 'data' in resp_json:
            signcount = resp_json['data']['signcount']
            signpoint = resp_json['data']['signpoint']

        message = '签到信息: ' + msg
        if signcount != 0 and signpoint != 0:
            message = message + ' 签到总天数: ' + str(signcount)
        return message, True

    def ablesci_checkin_main(self):
        if self.cookie is not None and len(self.cookie) > 0:
            account_checkin_message, success = self.__able_sci_checkin_withoutDriver__()
            # 存在账户签到信息，说明成功执行了签到
            if account_checkin_message is not None and len(account_checkin_message) > 0:
                log_info(f"[Ableaci_Account_{self.account_index}]:" + str(account_checkin_message), my_logger=self.logger)
                # self.checkin_message.append(f"[Ableaci_Account_{self.account_index}] checkin message:" + str(account_checkin_message) + "      \n")
        else:
            return '', False
        return f"[Ableaci_Account_{self.account_index}] " + str(account_checkin_message) + "      \n", success

    def able_sci_sign(self):

        if self.checkin_verification is None or self.checkin_verification == '':
            return ''.join(self.checkin_message), False
        success = False
        try:
            # 科研通签到
            log_info('*******************************able_sci checkin*******************************', my_logger=self.logger)
            if isinstance(self.checkin_verification, str) is True:
                self.cookie = self.checkin_verification
                self.account_index = 1
                message, success = self.ablesci_checkin_main()
                self.checkin_message.append(message)
            elif isinstance(self.checkin_verification, list) is True:
                for i in range(0, len(self.checkin_verification)):
                    if isinstance(self.checkin_verification[i], dict) is True:
                        self.cookie = self.checkin_verification[i]['cookie']
                        self.account_index = i + 1
                        message, success = self.ablesci_checkin_main()
                        self.checkin_message.append(message)
                    else:
                        log_info('able_sci config error', my_logger=self.logger)
                        self.checkin_message.append('able_sci config error')

                    if self.more_time_sleep > 0:
                        time.sleep(self.more_time_sleep)
            else:
                log_info('able_sci config error' + '    \n', my_logger=self.logger)
                self.checkin_message.append('able_sci config error' + '    \n')

            log_info('*******************************able_sci checkin complete*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), success
        except Exception as e:
            self.checkin_message.append('main function: able_sci checkin error, the error is ' + str(e) + '    \n')
            log_info('main function: able_sci checkin error, the error is ' + str(e) + '    \n', my_logger=self.logger)
            log_info('*******************************able_sci error*******************************', my_logger=self.logger)

        return ''.join(self.checkin_message), True
