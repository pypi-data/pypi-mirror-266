#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: 52pojie.py
Author: WFRobert
Date: 2023/3/9 15:01
cron: 6 14 9 * * ?
new Env('52pojie自动签到脚本');
Description: 52pojie自动签到,实现每日自动签到52pojie
Update: 2023/3/9 更新cron
"""
import os
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup

from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.checkin_util.logutil import log_info
from yaoys_checkin.model.all_class_parent import allClassParent


class wuaipojie_checkin(allClassParent):
    def __init__(self, **kwargs):
        super(wuaipojie_checkin, self).__init__(**kwargs)

        self.session = None
        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])

        self.cookie_dict = None

        self.checkin_message, self.is_success = self.wuaipojie_sign()

    def wuaipojie_sign(self):
        if self.checkin_verification is None or self.checkin_verification == '':
            return ''.join(self.checkin_message), False

        try:
            # 吾爱破解签到
            log_info('*******************************wuaipojie checkin*******************************', my_logger=self.logger)
            if isinstance(self.checkin_verification, str) is True:
                self.cookie = self.checkin_verification
                self.account_index = 1
                self.checkin_message.append(self.wuaipojie_checkin_main())
            elif isinstance(self.checkin_verification, list) is True:
                for i in range(0, len(self.checkin_verification)):
                    if isinstance(self.checkin_verification[i], dict) is True:
                        self.cookie = self.checkin_verification[i]['cookie']
                        self.account_index = i + 1
                        self.checkin_message.append(self.wuaipojie_checkin_main())
                    else:
                        log_info('wuaipojie config error' + '    \n', my_logger=self.logger)
                        self.checkin_message.append('wuaipojie config error' + '    \n')

                    if self.more_time_sleep > 0:
                        time.sleep(self.more_time_sleep)
            else:
                log_info('wuaipojie config error' + '    \n', my_logger=self.logger)
                self.checkin_message.append('wuaipojie config error' + '    \n')
            log_info('*******************************wuaipojie checkin complete*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), True
        except Exception as e:
            self.checkin_message.append('main function: wuaipojie checkin error, the error is ' + str(e) + '    \n')
            log_info('main function: wuaipojie checkin error, the error is ' + str(e) + '    \n', my_logger=self.logger)
            log_info('*******************************wuaipojie error*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), False

    def wuaipojie_checkin_main(self):
        message = ''
        url1 = "https://www.52pojie.cn/CSPDREL2hvbWUucGhwP21vZD10YXNrJmRvPWRyYXcmaWQ9Mg==?wzwscspd=MC4wLjAuMA=="
        url2 = 'https://www.52pojie.cn/home.php?mod=task&do=apply&id=2&referer=%2F'
        url3 = 'https://www.52pojie.cn/home.php?mod=task&do=draw&id=2'
        cookie = urllib.parse.unquote(self.cookie)
        cookie_list = cookie.split(";")
        cookie = ''
        self.session = requests.sessions.session()
        for i in cookie_list:
            key = i.split("=")[0]
            if "htVC_2132_saltkey" in key:
                cookie += "htVC_2132_saltkey=" + urllib.parse.quote(i.split("=")[1]) + "; "
            if "htVC_2132_auth" in key:
                cookie += "htVC_2132_auth=" + urllib.parse.quote(i.split("=")[1]) + ";"
        if not ('htVC_2132_saltkey' in cookie or 'htVC_2132_auth' in cookie):
            # log_error(f"cookie中未包含htVC_2132_saltkey或htVC_2132_auth字段，请检查cookie", my_logger=self.logger)
            message = f"cookie中未包含htVC_2132_saltkey或htVC_2132_auth字段，请检查cookie"
            return f"[wuaipojie_Account_{self.account_index}] " + message
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                      "application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/109.0.0.0 Safari/537.36",
        }
        r = self.session.get(url1, headers=headers, allow_redirects=False)
        s_cookie = r.headers['Set-Cookie']
        cookie = cookie + s_cookie
        headers['Cookie'] = cookie
        time.sleep(self.time_sleep)
        r = self.session.get(url2, headers=headers, allow_redirects=False)
        s_cookie = r.headers['Set-Cookie']
        cookie = cookie + s_cookie
        headers['Cookie'] = cookie
        time.sleep(self.time_sleep)
        r = self.session.get(url3, headers=headers)
        r_data = BeautifulSoup(r.text, "html.parser")
        jx_data = r_data.find("div", id="messagetext").find("p").text
        if "您需要先登录才能继续本操作" in jx_data:
            # log_error(f"第😢{n}个账号Cookie 失效", my_logger=self.logger)
            message = f"账号Cookie 失效"
        elif "恭喜" in jx_data:
            # log_info(f"😊第{n}个账号签到成功", my_logger=self.logger)
            message = f"账号签到成功"
        elif "不是进行中的任务" in jx_data:
            # log_info(f"😊第{n}个账号今日已签到", my_logger=self.logger)
            message = f"账号今日已签到"
        else:
            # log_info(f"😢第{n}个账号签失败", my_logger=self.logger)
            message = f"账号签到失败"

        return f"[wuaipojie_Account_{self.account_index}] " + message + '\n'
