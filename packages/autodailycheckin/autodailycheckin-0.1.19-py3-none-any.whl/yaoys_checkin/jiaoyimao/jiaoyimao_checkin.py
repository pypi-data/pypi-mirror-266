# -*- coding: utf-8 -*-
# @FileName  :jiaoyimao_checkin.py
# @Time      :2023/7/5 17:42
# @Author    :yaoys
# @Desc      : 交易猫签到
import json
import os
import time

import requests
from requests.cookies import cookiejar_from_dict

from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.checkin_util.logutil import log_error, log_info
from yaoys_checkin.model.all_class_parent import allClassParent


class jiaoyimao(allClassParent):
    def __init__(self, **kwargs):
        super(jiaoyimao, self).__init__(**kwargs)

        # 交易猫链接配置
        self.session = None
        self.JiaoYiMao_Api = "https://m.jiaoyimao.com"
        self.JiaoYiMao_Url = self.JiaoYiMao_Api + "/api2/account/integration/getMyIntegration"
        self.JiaoYiMao_SginUrl = self.JiaoYiMao_Api + "/api2/account/integration/signin"
        self.JiaoYiMao_Referer = self.JiaoYiMao_Api + "/account/integration/center?spm=gcmall.home2022.topshortcut.0"

        self.account_checkin_message = ''
        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])

        self.checkin_message, self.is_success = self.jiaoyimao_sign()
        # self.get_checkin_message()

    def jiaoyimao_sign(self):
        if self.checkin_verification is None or self.checkin_verification == '':
            return ''.join(self.checkin_message), False
        is_success = False
        try:
            log_info('**********************************jiaoyimao checkin***************************************', my_logger=self.logger)
            if self.checkin_verification is not None and len(self.checkin_verification) > 0:
                if isinstance(self.checkin_verification, str) is True:
                    self.cookie = self.checkin_verification
                    self.account_index = 1
                    message, is_success = self.jiaoyimao_checkin()
                    self.checkin_message.append(message)
                elif isinstance(self.checkin_verification, list) is True:
                    for i in range(0, len(self.checkin_verification)):
                        if isinstance(self.checkin_verification[i], dict) is True:
                            self.cookie = self.checkin_verification[i]['cookie']
                            self.account_index = i + 1
                            message, is_success = self.jiaoyimao_checkin()
                            self.checkin_message.append(message)
                        else:
                            log_info('jiaoyimao config error' + '    \n', my_logger=self.logger)
                            self.checkin_message.append('jiaoyimao config error' + '    \n')

                        if self.more_time_sleep > 0:
                            time.sleep(self.more_time_sleep)
            log_info(''.join(self.checkin_message), my_logger=self.logger)
            log_info('**********************************jiaoyimao checkin complete***************************************', my_logger=self.logger)
            return ''.join(self.checkin_message), is_success
        except Exception as e:
            log_info('jiaoyimao checkin error' + str(e) + '    \n', my_logger=self.logger)
            self.checkin_message.append('main function: jiaoyimao checkin error, the error is ' + str(e) + '    \n')
            log_info('*******************************jiaoyimao error*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), False

    def jiaoyimao_checkin(self):
        head = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "referer": self.JiaoYiMao_Referer,
            "x-csrf-token": "HT-x5YUi3IF7iyVDXY6FBc6g",
            "x-requested-with": "com.jym.mall"
        }
        self.session = requests.sessions.session()
        cookie_dict = {i.split("=")[0]: i.split("=")[1] for i in self.cookie.split("; ")}
        try:
            zz = self.session.get(url=self.JiaoYiMao_SginUrl, cookies=cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True), headers=head)
            if "<script>" in zz.text:
                return f"[Jiaoyimao_Account_{self.account_index}]: cookie可能已过期，请更新cookie重新尝试签到\n", False

            if json.loads(zz.text)['success'] is True:
                time.sleep(self.time_sleep)
                rep = self.session.get(url=self.JiaoYiMao_Url, cookies=cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True), headers=head)
                if json.loads(rep.text)['stateCode'] == 200:
                    Integral = json.loads(rep.text)['data']['amountLeft']
                else:
                    Integral = "获取积分失败"
                # log_info(f"交易猫:签到成功 - 现有积分{Integral}", my_logger=self.logger)
                return f"[Jiaoyimao_Account_{self.account_index}]: 签到成功 - 现有积分: {Integral}\n", True
            elif '"success":false' in zz.text and '活动太火爆了，请稍后重试' in zz.text:
                return f"[Jiaoyimao_Account_{self.account_index}]: 签到失败 - 已经签到了\n", True
            else:
                # log_info(f"交易猫:签到失败 - 已经签到了", my_logger=self.logger)
                return f"[Jiaoyimao_Account_{self.account_index}]: 发生未知错误，请联系开发者\n", False
        except Exception as e:
            log_error(e, my_logger=self.logger)
            # log_info("交易猫:cookie可能已过期，或出现了错误", my_logger=self.logger)
            return f"[Jiaoyimao_Account_{self.account_index}]: 发生未知错误，请查看log日志\n", False
