import os
import time

import requests
import urllib3

from yaoys_checkin.checkin_util.logutil import log_info
from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.model.all_class_parent import allClassParent

bilbi_checkin_url = 'https://www.bilibili.com/'
bilibili_coin_count_url = 'https://account.bilibili.com/site/getCoin?csrf=66d56f905a20735f69bf816d2d867e83'
bilibili_coin_log_url = 'https://api.bilibili.com/x/member/web/coin/log?csrf=66d56f905a20735f69bf816d2d867e83&jsonp=jsonp'

# 解决出现警告 Adding certificate verification is strongly advised.
urllib3.disable_warnings()


class bilibili_coin(allClassParent):
    def __init__(self, **kwargs):
        super(bilibili_coin, self).__init__(**kwargs)

        self.session = None
        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])

        self.checkin_message, self.is_success = self.bilibili_coin_sign()

        # self.get_checkin_message()

    def __get_header(self):
        header = {
            'Connection': 'Keep-Alive',
            'Accept': '*/*',
            'Accept-Language': 'zh-cn',
            'Cookie': self.cookie,
            'Content-Type': 'application/json;charset=UTF-8',
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv)"
                          " AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74"
                          ".0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clie"
                          "ntId/355325117317828 clientModel/SM-G930K imsi/46007111431782"
                          "4 clientChannelId/qq proVersion/1.0.6",
            "Accept-Encoding": "gzip, deflate",
        }
        return header

    def __get_coin_count_header(self):
        header = {
            'Connection': 'Keep-Alive',
            'Accept': '*/*',
            'Accept-Language': 'zh-cn',
            'Cookie': self.cookie,
            'referer': 'https://account.bilibili.com/account/coin',
            'Content-Type': 'application/json;charset=UTF-8',
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv)"
                          " AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74"
                          ".0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clie"
                          "ntId/355325117317828 clientModel/SM-G930K imsi/46007111431782"
                          "4 clientChannelId/qq proVersion/1.0.6",
            "Accept-Encoding": "gzip, deflate",
        }
        return header

    def __get_coin_log_header(self):
        header = {
            'Connection': 'Keep-Alive',
            'Accept': '*/*',
            'Accept-Language': 'zh-cn',
            'Cookie': self.cookie,
            'referer': 'https://account.bilibili.com/',
            'Content-Type': 'application/json;charset=UTF-8',
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv)"
                          " AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74"
                          ".0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clie"
                          "ntId/355325117317828 clientModel/SM-G930K imsi/46007111431782"
                          "4 clientChannelId/qq proVersion/1.0.6",
            "Accept-Encoding": "gzip, deflate",
        }
        return header

    def bilibili_checkin(self):
        self.session = requests.sessions.session()
        header = self.__get_header()
        resp = self.session.get(url=bilbi_checkin_url, headers=header, verify=False)
        resp_code = resp.status_code
        resp.close()
        check_message = ''
        if resp_code == 200:
            # get coin count
            header = self.__get_coin_count_header()
            time.sleep(self.time_sleep)
            resp = self.session.get(url=bilibili_coin_count_url, headers=header, verify=False)
            if resp.json()['code'] == 0:
                check_message = '硬币总数: {}, '.format(resp.json()['data']['money'])
            elif 'code' in resp.text and resp.json()['code'] == -101:
                check_message = '获取硬币数量错误: code=' + str(resp.json()['code']) + ',cookie过期，请更新cookie'

            resp.close()

            # get coin log and latest log
            header = self.__get_coin_log_header()
            time.sleep(self.time_sleep)
            resp = self.session.get(url=bilibili_coin_log_url, headers=header, verify=False)
            if resp.json()['code'] == 0 and resp.json()['message'] == '0':
                check_message += ' 硬币最新记录： 在 {} 通过 {} 硬币数量增加/减少 {}'.format(resp.json()['data']['list'][0]['time'],
                                                                                            resp.json()['data']['list'][0]['reason'],
                                                                                            resp.json()['data']['list'][0]['delta'])
            resp.close()

        else:
            check_message = '获取硬币数量错误，状态码: ' + str(resp_code)

        check_message = check_message
        return check_message

    def bilibili_checkin_main(self):
        if self.cookie is not None and len(self.cookie) > 0:
            account_checkin_message = self.bilibili_checkin()

            # 存在账户签到信息，说明成功执行了签到
            if account_checkin_message is not None and len(account_checkin_message) > 0:
                log_info(f"[Bilibili_Account_{self.account_index}]:" + str(account_checkin_message), my_logger=self.logger)
                self.checkin_message.append(f"[Bilibili_Account_{self.account_index}] :" + str(account_checkin_message) + "      \n")
        return self.checkin_message

    def bilibili_coin_sign(self):

        if self.checkin_verification is None or self.checkin_verification == '':
            return ''.join(self.checkin_message), False
        try:
            # bilibili请求,获取硬币
            log_info('*******************************bilibili_coin checkin*******************************', my_logger=self.logger)
            if isinstance(self.checkin_verification, str) is True:
                self.cookie = self.checkin_verification
                self.account_index = 1
                self.checkin_message = self.bilibili_checkin_main()
            elif isinstance(self.checkin_verification, list) is True:
                for i in range(0, len(self.checkin_verification)):
                    if isinstance(self.checkin_verification[i], dict) is True:
                        self.cookie = self.checkin_verification[i]['cookie']
                        self.account_index = i + 1
                        self.checkin_message = self.bilibili_checkin_main()
                    else:
                        log_info('bilibili_coin config error' + '    \n', my_logger=self.logger)
                        self.checkin_message.append('bilibili_coin config error' + '    \n')

                    if self.more_time_sleep > 0:
                        time.sleep(self.more_time_sleep)
            else:
                log_info('bilibili_coin config error' + '    \n', my_logger=self.logger)
                self.checkin_message.append('bilibili_coin config error' + '    \n')
            log_info('*******************************bilibili_coin checkin complete*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), True
        except Exception as e:
            self.checkin_message.append('main function: bilibili checkin error, the error is ' + str(e) + '    \n')
            log_info('main function: bilibili checkin error, the error is ' + str(e) + '    \n', my_logger=self.logger)
            log_info('*******************************bilibili_coin error*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), False
