# -*- coding: utf-8 -*-
# @FileName  :gufen_checkin.py
# @Time      :2022/12/30 12:22
# @Author    :yaoys
# @Desc      :
import os
import re
import time

import requests
import urllib3
from bs4 import BeautifulSoup
from requests.cookies import cookiejar_from_dict

from yaoys_checkin.checkin_util.logutil import log_info
from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.model.all_class_parent import allClassParent

header = {
    'Host': 'bbs.99lb.net',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer': 'http://bbs.99lb.net/',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
}
count_header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'max-age=0',
    'Host': 'bbs.99lb.net',
    'Referer': 'http://bbs.99lb.net/cuid-127194.html',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}


class gufenxueshu(allClassParent):
    def __init__(self, **kwargs):
        super(gufenxueshu, self).__init__(**kwargs)

        self.session = None
        self.__gufen_checkin_url = 'http://bbs.99lb.net/plugin.php?id=are_sign:getaward&typeid=1'
        self.count_url = 'http://bbs.99lb.net/home.php?mod=spacecp&ac=credit'

        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])

        self.checkin_message, self.is_success = self.gufen_sign()

    # 解决出现警告 Adding certificate verification is strongly advised.
    urllib3.disable_warnings()

    def __gufen_checkin(self):
        self.session = requests.sessions.session()
        cookie_dict = {i.split("=")[0]: i.split("=")[1] for i in self.cookie.split("; ")}
        resp = self.session.get(url=self.__gufen_checkin_url,
                                cookies=cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True),
                                headers=header,
                                timeout=10,
                                verify=False)
        resp_code = resp.status_code
        checkin_message = ''
        if resp_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            result = soup.find_all('div', attrs={'id': 'messagetext'})
            for res in result:
                checkin_message = res.find_next(name='p').text
                break
            # 获取总积分
            time.sleep(self.time_sleep)
            resp = self.session.get(url=self.count_url,
                                    cookies=cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True),
                                    headers=header,
                                    timeout=10,
                                    verify=False)
            if resp.status_code == 200:
                s = re.findall(r'<li class="ren_zjfs"><em>(.*?) </em>(.*?)<span class="xg1">(.*?)</span></li>', resp.text)
                if len(s) > 0 and len(s[0]) > 2:
                    checkin_message = checkin_message + ', 当前总积分：' + s[0][1]
            else:
                checkin_message = checkin_message + ',获取总积分失败'
        else:
            checkin_message = 'checkin error,the status code is ' + str(resp_code)
        resp.close()
        return checkin_message

    def gufen_checkin_main(self):
        if self.cookie is not None and len(self.cookie) > 0:
            account_checkin_message = self.__gufen_checkin()
            # 存在账户签到信息，说明成功执行了签到
            if account_checkin_message is not None and len(account_checkin_message) > 0:
                log_info(f"[gufen_Account_{self.account_index}]:" + str(account_checkin_message), my_logger=self.logger)
                self.checkin_message.append(f"[gufen_Account_{self.account_index}] :" + str(account_checkin_message) + "      \n")
        return self.checkin_message

    def gufen_sign(self):
        if self.checkin_verification is None or self.checkin_verification == '':
            return ''.join(self.checkin_message), False

        try:
            # 谷粉学术签到
            log_info('*******************************gufen checkin*******************************', my_logger=self.logger)
            if isinstance(self.checkin_verification, str) is True:
                self.cookie = self.checkin_verification
                self.account_index = 1
                self.checkin_message = self.gufen_checkin_main()
            elif isinstance(self.checkin_verification, list) is True:
                for i in range(0, len(self.checkin_verification)):
                    if isinstance(self.checkin_verification[i], dict) is True:
                        self.cookie = self.checkin_verification[i]['cookie']
                        self.account_index = i + 1
                        self.checkin_message = self.gufen_checkin_main()
                    else:
                        log_info('gufen config error' + '    \n', my_logger=self.logger)
                        self.checkin_message.append('gufen config error' + '    \n')

                    if self.more_time_sleep > 0:
                        time.sleep(self.more_time_sleep)
            else:
                log_info('gufen config error' + '    \n', my_logger=self.logger)
                self.checkin_message.append('gufen config error' + '    \n')
            log_info('*******************************gufen checkin complete*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), True
        except Exception as e:
            self.checkin_message.append('main function: gufenxueshu checkin error, the error is ' + str(e) + '    \n')
            log_info('main function: gufenxueshu checkin error, the error is ' + str(e) + '    \n', my_logger=self.logger)
            log_info('*******************************gufen error*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), False
