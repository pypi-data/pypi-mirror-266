import hashlib
import json
import os
import re
import time

import requests
from requests.cookies import cookiejar_from_dict

from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.checkin_util.logutil import log_info
from yaoys_checkin.model.all_class_parent import allClassParent


class tieba(allClassParent):
    def __init__(self, **kwargs):
        super(tieba, self).__init__(**kwargs)

        self.session = None
        self.__login_info = 'https://zhidao.baidu.com/api/loginInfo'

        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])

        self.cookie_dict = None

        self.checkin_message, self.is_success = self.tieba_sign()

    def login_info(self):
        return self.session.get(url=self.__login_info, cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True)).json()

    def valid(self):
        try:
            content = self.session.get(url="https://tieba.baidu.com/dc/common/tbs", cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True))
        except Exception as e:
            return False, f"登录验证异常,错误信息: {e}"
        data = json.loads(content.text)
        if data["is_login"] == 0:
            return False, "登录失败,cookie 异常"
        tbs = data["tbs"]
        user_name = self.login_info()["userName"]
        return tbs, user_name

    def tieba_list_more(self):
        content = self.session.get(url="https://tieba.baidu.com/f/like/mylike?&pn=1", timeout=5, allow_redirects=False, cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True))
        try:
            pn = int(re.match(r".*/f/like/mylike\?&pn=(.*?)\">尾页.*", content.text, re.S | re.I).group(1))
        except Exception as e:
            pn = 1
        next_page = 1
        pattern = re.compile(r".*?<a href=\"/f\?kw=.*?title=\"(.*?)\">")
        while next_page <= pn:
            tbname = pattern.findall(content.text)
            for x in tbname:
                yield x
            next_page += 1
            content = self.session.get(
                url=f"https://tieba.baidu.com/f/like/mylike?&pn={next_page}", timeout=5, allow_redirects=False, cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True)
            )

    def __tieba_sign(self, tb_name_list, tbs):
        success_count, error_count, exist_count, shield_count = 0, 0, 0, 0
        for tb_name in tb_name_list:
            md5 = hashlib.md5(f"kw={tb_name}tbs={tbs}tiebaclient!!!".encode("utf-8")).hexdigest()
            data = {"kw": tb_name, "tbs": tbs, "sign": md5}
            time.sleep(self.time_sleep)
            try:
                response = self.session.post(url="https://c.tieba.baidu.com/c/c/forum/sign",
                                             data=data,
                                             verify=False,
                                             cookies=cookiejar_from_dict(self.cookie_dict, cookiejar=None, overwrite=True)).json()
                if response["error_code"] == "0":
                    success_count += 1
                elif response["error_code"] == "160002":
                    exist_count += 1
                elif response["error_code"] == "340006":
                    shield_count += 1
                else:
                    error_count += 1
            except Exception as e:
                print(f"贴吧 {tb_name} 签到异常,原因{str(e)}")
        msg = [
            {"name": "贴吧总数", "value": len(tb_name_list)},
            {"name": "签到成功", "value": success_count},
            {"name": "已经签到", "value": exist_count},
            {"name": "被屏蔽的", "value": shield_count},
            {"name": "签到失败", "value": error_count},
        ]
        return msg

    def get_tieba_list(self):
        tieba_list = list(self.tieba_list_more())
        return tieba_list

    def tieba_checkin_main(self):
        self.session = requests.sessions.session()
        self.cookie_dict = {item.split("=")[0]: item.split("=")[1] for item in self.cookie.split("; ")}
        self.session.headers.update({"Referer": "https://www.baidu.com/"})
        tbs, user_name = self.valid()
        if tbs:
            tb_name_list = self.get_tieba_list()
            time.sleep(self.time_sleep)
            msg = self.__tieba_sign(tb_name_list=tb_name_list, tbs=tbs)
            msg = [{"name": "帐号信息", "value": user_name}] + msg
        else:
            msg = [
                {"name": "帐号信息", "value": user_name},
                {"name": "签到信息", "value": "Cookie 可能过期"},
            ]
        msg = "\t".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return f"[tieba_Account_{self.account_index}] " + msg + '\n'

    def tieba_sign(self):
        if self.checkin_verification is None or self.checkin_verification == '':
            return ''.join(self.checkin_message), False

        try:
            # 百度贴吧签到
            log_info('*******************************tieba checkin*******************************', my_logger=self.logger)
            if isinstance(self.checkin_verification, str) is True:
                self.cookie = self.checkin_verification
                self.account_index = 1
                self.checkin_message.append(self.tieba_checkin_main())
            elif isinstance(self.checkin_verification, list) is True:
                for i in range(0, len(self.checkin_verification)):
                    if isinstance(self.checkin_verification[i], dict) is True:
                        self.cookie = self.checkin_verification[i]['cookie']
                        self.account_index = i + 1
                        self.checkin_message.append(self.tieba_checkin_main())
                    else:
                        log_info('tieba config error' + '    \n', my_logger=self.logger)
                        self.checkin_message.append('tieba config error' + '    \n')
                        return ''.join(self.checkin_message), False

                    if self.more_time_sleep > 0:
                        time.sleep(self.more_time_sleep)
            else:
                log_info('tieba config error' + '    \n', my_logger=self.logger)
                self.checkin_message.append('tieba config error' + '    \n')
                return ''.join(self.checkin_message), False
            log_info(''.join(self.checkin_message), my_logger=self.logger)
            log_info('*******************************tieba checkin complete*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), True
        except Exception as e:
            self.checkin_message.append('main function: tieba checkin error, the error is ' + str(e) + '    \n')
            log_info('main function: tieba checkin error, the error is ' + str(e) + '    \n', my_logger=self.logger)
            log_info('*******************************tieba error*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), False
