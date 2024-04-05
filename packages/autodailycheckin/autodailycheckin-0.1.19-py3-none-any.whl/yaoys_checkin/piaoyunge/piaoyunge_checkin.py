# -*- coding: utf-8 -*-
# @FileName  :piaoyunge_checkin.py
# @Time      :2023/7/10 21:14
# @Author    :yaoys
# @Desc      : 飘云阁签到，先获取formhash参数值，在执行签到
import os
import re
import time
import warnings

import requests
from requests.cookies import cookiejar_from_dict

from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.checkin_util.logutil import log_info
from yaoys_checkin.model.all_class_parent import allClassParent

warnings.filterwarnings('ignore')

get_fromhash_header = {
    'Host': 'www.chinapyg.com',
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': 'Windows',
    'Accept': '*/*',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.chinapyg.com/forum.php?mod=viewthread&tid=147569&page=1',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}

sign_header = {
    'Host': 'www.chinapyg.com',
    'Content-Length': '56',
    'Origin': 'https://www.chinapyg.com',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Referer': 'https://www.chinapyg.com/forum-83-1.html',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}


class piaoyunge(allClassParent):
    def __init__(self, **kwargs):
        super(piaoyunge, self).__init__(**kwargs)

        self.session = None
        self.cookie_dict = None
        self.account_checkin_message = ''
        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])
        self.from_hash = None
        self.checkin_message, self.is_success = self.piaoyunge_sign()
        # self.get_checkin_message()

    def __get_fromhash__(self):
        resp = self.session.post(url='https://www.chinapyg.com/plugin.php?id=dsu_paulsign:sign&infloat=yes&handlekey=dsu_paulsign&inajax=1&ajaxtarget=fwin_content_dsu_paulsign',
                                 headers=get_fromhash_header,
                                 verify=False,
                                 cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True),
                                 # data=data,
                                 timeout=5)
        if resp.status_code != 200:
            self.from_hash = 'fromhash获取失败'
            return False
        else:
            if '您今天已经签到过了或者签到时间还未开始' in resp.text:
                self.from_hash = '您今天已经签到过了或者签到时间还未开始'
                return False
            s = re.findall(r'<input type="hidden" name="formhash" value="(.*?)">', resp.text)
            if s is None or len(s) <= 0 or len(s) != 1:
                self.from_hash = 'fromhash获取失败'
                return False
            else:
                self.from_hash = s[0]
                return True

    def piaoyunge_checkin(self):
        self.session = requests.sessions.session()
        self.cookie_dict = {i.split("=")[0]: i.split("=")[1] for i in self.cookie.split("; ")}
        is_success = self.__get_fromhash__()
        if is_success is False:
            return f"[Piaoyunge_Account_{self.account_index}]: 签到失败，{self.from_hash}\n"

        time.sleep(self.time_sleep)
        data = {
            'formhash': self.from_hash,
            'qdxq': 'kx',
            'qdmode': '2',
            'todaysay': '',
            'fastreply': '0'
        }
        resp = self.session.post(url='https://www.chinapyg.com/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&sign_as=1&inajax=1',
                                 headers=sign_header,
                                 verify=False,
                                 cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True),
                                 data=data,
                                 timeout=5)
        if resp.status_code == 200:
            s = re.findall(r'<div class="c">(.*?)</div>', resp.text.replace('\n', ''))
            if s is not None and len(s) == 1:
                return f"[Piaoyunge_Account_{self.account_index}]: '签到完毕，{s[0]}\n"
        else:
            return f"[Piaoyunge_Account_{self.account_index}]: '签到失败，{resp.text}\n"

    def piaoyunge_sign(self):
        if self.checkin_verification is None or self.checkin_verification == '':
            return ''.join(self.checkin_message), False

        try:
            log_info('**********************************飘云阁执行签到***************************************', my_logger=self.logger)
            if self.checkin_verification is not None and len(self.checkin_verification) > 0:
                if isinstance(self.checkin_verification, str) is True:
                    self.cookie = self.checkin_verification
                    self.account_index = 1
                    self.checkin_message.append(self.piaoyunge_checkin())
                elif isinstance(self.checkin_verification, list) is True:
                    for i in range(0, len(self.checkin_verification)):
                        if isinstance(self.checkin_verification[i], dict) is True:
                            self.cookie = self.checkin_verification[i]['cookie']
                            self.account_index = i + 1
                            self.checkin_message.append(self.piaoyunge_checkin())
                        else:
                            log_info('飘云阁配置文件错误' + '    \n', my_logger=self.logger)
                            self.checkin_message.append('飘云阁配置文件错误' + '    \n')

                        if self.more_time_sleep > 0:
                            time.sleep(self.more_time_sleep)
            log_info(''.join(self.checkin_message), my_logger=self.logger)
            log_info('**********************************飘云阁签到执行完毕***************************************', my_logger=self.logger)
            return ''.join(self.checkin_message), True
        except Exception as e:
            log_info('飘云阁签到错误' + str(e) + '    \n', my_logger=self.logger)
            self.checkin_message.append('main function: 飘云阁配置文件错误，错误信息：' + str(e) + '    \n')
            log_info('*******************************飘云阁签到错误*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), False
