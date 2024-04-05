# -*- coding: utf-8 -*-
# @FileName  :piaoyunge_checkin.py
# @Time      :2023/7/10 21:14
# @Author    :yaoys
# @Desc      : leado签到，先获取formhash参数值，在执行签到 https://legado.cn/
import os
import re
import time
import warnings

import requests
from requests.cookies import cookiejar_from_dict

from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.checkin_util.logutil import log_info
from yaoys_checkin.model.all_class_parent import allClassParent
from bs4 import BeautifulSoup

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Host': 'legado.cn',
    'Referer': 'https://legado.cn/k_misign-sign.html',
    'Sec-Ch-Ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': 'Windows',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
}

warnings.filterwarnings('ignore')


class Leado(allClassParent):
    def __init__(self, **kwargs):
        super(Leado, self).__init__(**kwargs)

        self.session = None
        self.cookie_dict = None
        self.account_checkin_message = ''
        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])
        self.from_hash = None
        self.checkin_message, self.is_success = self.leado_sign()
        # self.get_checkin_message()

    def __get_fromhash__(self):
        resp = self.session.get(url='https://legado.cn/k_misign-sign.html',
                                headers=headers,
                                verify=False,
                                cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True),
                                # data=data,
                                timeout=5)
        if resp.status_code != 200:
            self.from_hash = 'fromhash获取失败'
            return False
        else:
            s = re.findall(r'formhash=(.*?)">退出</a></li>', resp.text)
            if s is None or len(s) <= 0 or len(s) != 1:
                self.from_hash = 'fromhash获取失败'
                return False
            else:
                self.from_hash = s[0]
                return True

    def leado_checkin(self):
        self.session = requests.sessions.session()
        self.cookie_dict = {i.split("=")[0]: i.split("=")[1] for i in self.cookie.split("; ")}
        is_success = self.__get_fromhash__()
        if is_success is False:
            return f"[Leado_Account_{self.account_index}]: 签到失败，{self.from_hash}\n"

        data = {
            'formhash': self.from_hash,
            'id': 'k_misign:sign',
            'operation': 'qiandao',
            'format': 'empty',
            'inajax': 1,
            'ajaxtarget': ''
        }
        resp = self.session.post(url='https://legado.cn/plugin.php',
                                 headers=headers,
                                 verify=False,
                                 cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True),
                                 data=data,
                                 timeout=5)
        # resp = self.session.post(url='https://legado.cn/k_misign-sign.html',
        #                          headers=headers,
        #                          verify=False,
        #                          cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True),
        #                          # data=data,
        #                          timeout=5)

        if resp.status_code == 200:
            checkin_message = "签到成功,"
            resp = self.session.post(url='https://legado.cn/k_misign-sign.html',
                                     headers=headers,
                                     verify=False,
                                     cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True),
                                     # data=data,
                                     timeout=5)
            # 获取用户名
            bs = BeautifulSoup(resp.text, "html.parser")
            username = bs.find('a', id='myitem').get_text()
            checkin_message += "用户名:" + username + ","
            # 连续签到天数
            lxdays = bs.find('input', id='lxdays').attrs['value']
            checkin_message += "连续签到天数:" + lxdays + ','
            # 签到等级
            lxlevel = bs.find('input', id='lxlevel').attrs['value']
            checkin_message += "签到等级:" + lxlevel + ','
            # 积分奖励
            lxreward = bs.find('input', id='lxreward').attrs['value']
            checkin_message += "积分奖励:" + lxreward + ','
            # 总天数
            lxtdays = bs.find('input', id='lxtdays').attrs['value']
            checkin_message += "总天数:" + lxtdays
            # #
            # resp = self.session.get(url='https://legado.cn/plugin.php?id=k_misign:sign&operation=list&inajax=1&ajaxtarget=ranklist',
            #                         headers=headers,
            #                         verify=False,
            #                         cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True),
            #                         # data=data,
            #                         timeout=5)
            # bs = BeautifulSoup(resp.text, "html.parser")
            # table = bs.find("table", id="J_list_detail")
            #
            # has_time = False
            # for tr in table.find_all("tr"):
            #     if has_time is True:
            #         break
            #     for a in tr.find_all("a"):
            #         if a.text == username:
            #             last_sign_time = tr.find_all("td")[3]
            #             has_time = True
            #             break

            return f"[Leado_Account_{self.account_index}]: {checkin_message}"
        else:
            return f"[Leado_Account_{self.account_index}]: '签到失败，{resp.text}\n"

    def leado_sign(self):
        if self.checkin_verification is None or self.checkin_verification == '':
            return ''.join(self.checkin_message), False

        try:
            log_info('**********************************Leado执行签到***************************************', my_logger=self.logger)
            if self.checkin_verification is not None and len(self.checkin_verification) > 0:
                if isinstance(self.checkin_verification, str) is True:
                    self.cookie = self.checkin_verification
                    self.account_index = 1
                    self.checkin_message.append(self.leado_checkin())
                elif isinstance(self.checkin_verification, list) is True:
                    for i in range(0, len(self.checkin_verification)):
                        if isinstance(self.checkin_verification[i], dict) is True:
                            self.cookie = self.checkin_verification[i]['cookie']
                            self.account_index = i + 1
                            self.checkin_message.append(self.leado_checkin())
                        else:
                            log_info('Leado配置文件错误' + '    \n', my_logger=self.logger)
                            self.checkin_message.append('Leado配置文件错误' + '    \n')

                        if self.more_time_sleep > 0:
                            time.sleep(self.more_time_sleep)
            log_info(''.join(self.checkin_message), my_logger=self.logger)
            log_info('**********************************Leado签到执行完毕***************************************', my_logger=self.logger)
            return ''.join(self.checkin_message), True
        except Exception as e:
            log_info('Leado签到错误' + str(e) + '    \n', my_logger=self.logger)
            self.checkin_message.append('main function:Leado配置文件错误，错误信息：' + str(e) + '    \n')
            log_info('*******************************Leado签到错误*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), False
