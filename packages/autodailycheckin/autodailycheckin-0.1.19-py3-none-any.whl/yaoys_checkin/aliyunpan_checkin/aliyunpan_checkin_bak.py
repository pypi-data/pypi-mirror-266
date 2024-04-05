import os
import time
from datetime import datetime
from os import environ
from time import mktime

from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.checkin_util.logutil import log_info
from yaoys_checkin.model.all_class_parent import allClassParent


class aliyunpan(allClassParent):
    def __init__(self, **kwargs):
        super(aliyunpan, self).__init__(**kwargs)
        self.access_token = None
        self.expired_at = None
        self.phone = None
        self.account_checkin_message = ''

        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])

        self.checkin_message, self.is_success = self.aliyunpan_sign()
        # self.get_checkin_message()

    def get_access_token(self):
        data = self.session.post(
            'https://auth.aliyundrive.com/v2/account/token',
            json={
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
            }
        ).json()

        try:
            if 'code' in data:
                if data['code'] in [
                    'RefreshTokenExpired', 'InvalidParameter.RefreshToken',
                ]:
                    # log_info(f'[{refresh_token}] 获取 access token 失败, 错误信息: {data}', my_logger=checkin_logger)
                    self.account_checkin_message += f'RefreshToken已失效，请更新RefreshToken，获取 access token 失败, 错误信息: {data}\n'
                    # self.checkin_message.append(f'获取 access token 失败, 错误信息: {data}')
                    return False
        except KeyError as e:
            # log_info('阿里云盘获取access token 异常,' + str(e), my_logger=checkin_logger)
            self.account_checkin_message += 'RefreshToken已失效，请更新RefreshToken，阿里云盘获取access token 异常,' + str(e) + '\n'

        expire_time = datetime.strptime(data['expire_time'], '%Y-%m-%dT%H:%M:%SZ')

        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.expired_at = int((mktime(expire_time.timetuple())) + 8 * 60 * 60) * 1000
        self.phone = data['user_name']
        return {
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
            'expired_at': int((mktime(expire_time.timetuple())) + 8 * 60 * 60) * 1000,
            'phone': data['user_name'],
        }

    def sign_in(self):
        # 执行签到
        data = self.session.post(
            'https://member.aliyundrive.com/v2/activity/sign_in_list',
            headers={
                'Authorization': f'Bearer {self.access_token}',
            },
            json={},
        ).json()

        if 'success' not in data:
            # log_info(f'[{phone}] 签到失败, 错误信息: {data}', my_logger=checkin_logger)
            self.account_checkin_message += f'[{self.phone}] 签到失败, 错误信息: {data}\n'
            return False

        try:
            # 签到成功后领取奖励
            if 'result' in data and isinstance(data['result'], dict) is True:
                time.sleep(2)
                reward_data = self.session.post(
                    'https://member.aliyundrive.com/v1/activity/sign_in_reward',
                    params={'_rx-s': 'mobile'},
                    headers={'Authorization': f'Bearer {self.access_token}'},
                    json={'signInDay': data['result']['signInCount']},
                ).json()
                reward = (
                    '无奖励'
                    if not reward_data['success'] or reward_data is None
                    else f'获得 {reward_data["result"]["description"]},{reward_data["result"]["notice"]}'
                )
                # # log_info(f'[{phone}] 签到成功, 本月累计签到 {data["result"]["signInCount"]} 天.', my_logger=checkin_logger)
                # self.account_checkin_message += f'[{self.phone}] 签到成功, 本月累计签到 {data["result"]["signInCount"]} 天.'
                # # log_info(f'[{phone}] 本次签到 {reward}', my_logger=checkin_logger)
                # self.account_checkin_message += f' 本次签到{reward}'

                dailyTask = ""
                is_getDailyTask = False
                # 新版签到获取每日签到任务
                if 'signInInfos' in data['result'] and len(data['result']['signInInfos']) > 0:
                    signInInfos_array = data['result']['signInInfos']
                    # 遍历signInInfos
                    for i in range(len(signInInfos_array)):
                        # 得到最新签到的数据
                        if data["result"]["signInCount"] == int(signInInfos_array[i]['day']):
                            # 遍历今日签到详情
                            if 'rewards' in signInInfos_array[i]:
                                for j in range(len(signInInfos_array[i]['rewards'])):
                                    # 如果是每日签到任务
                                    if signInInfos_array[i]['rewards'][j]['type'] == 'dailyTask':
                                        dailyTask = signInInfos_array[i]['rewards'][j]['name'] + ',领取条件: ' + signInInfos_array[i]['rewards'][j]['remind'] + ',请前往APP完成并领取奖励'
                                        is_getDailyTask = True
                                        break
                        if is_getDailyTask is True:
                            break

                # log_info(f'[{phone}] 签到成功, 本月累计签到 {data["result"]["signInCount"]} 天.', my_logger=checkin_logger)
                self.account_checkin_message += f'[{self.phone}] 签到成功, 本月累计签到 {data["result"]["signInCount"]} 天.'
                # log_info(f'[{phone}] 本次签到 {reward}', my_logger=checkin_logger)
                self.account_checkin_message += f' 本次签到奖励: {reward}'
                if dailyTask != "":
                    self.account_checkin_message += f'. 签到任务奖励: {dailyTask}'
                return True
            else:
                return False
        except Exception as e:
            # log_info('aliyunpan sign error' + str(e), my_logger=checkin_logger)
            self.account_checkin_message += 'aliyunpan sign error' + str(e)

        return False

    def aliyun_checkin(self):

        self.account_checkin_message = ''
        self.account_checkin_message += f"[aliyun_Account_{self.account_index}]:"
        if self.refresh_token is not None and len(self.refresh_token) > 0:

            environ['NO_PROXY'] = '*'  # 禁止代理
            # 获取token
            data = self.get_access_token()
            if not data:
                return self.account_checkin_message
            time.sleep(2)
            # 签到
            if not self.sign_in():
                self.account_checkin_message += f'[{data["phone"]}] 签到失败.'
                log_info(f'[{data["phone"]}] 签到失败.', my_logger=self.logger)
                # self.checkin_message.append(self.account_checkin_message)
        else:
            self.account_checkin_message += 'The refresh_tokens is None'
        # self.checkin_message.append(''.join(message))
        self.account_checkin_message += '       \n'
        return self.account_checkin_message

    def aliyunpan_sign(self):
        if self.checkin_verification is None or self.checkin_verification == '':
            return ''.join(self.checkin_message), False

        try:
            log_info('**********************************aliyunpan checkin***************************************', my_logger=self.logger)
            if self.checkin_verification is not None and len(self.checkin_verification) > 0:
                if isinstance(self.checkin_verification, str) is True:
                    self.refresh_token = self.checkin_verification
                    self.account_index = 1
                    self.checkin_message.append(self.aliyun_checkin())
                elif isinstance(self.checkin_verification, list) is True:
                    for i in range(0, len(self.checkin_verification)):
                        if isinstance(self.checkin_verification[i], dict) is True:
                            self.refresh_token = self.checkin_verification[i]['cookie']
                            self.account_index = i + 1
                            self.checkin_message.append(self.aliyun_checkin())
                        else:
                            log_info('aliyunpan config error' + '    \n', my_logger=self.logger)
                            self.checkin_message.append('aliyunpan config error' + '    \n')

                        if self.more_time_sleep > 0:
                            time.sleep(self.more_time_sleep)
            log_info(''.join(self.checkin_message), my_logger=self.logger)
            log_info('**********************************aliyunpan checkin complete***************************************', my_logger=self.logger)
            return ''.join(self.checkin_message), True
        except Exception as e:
            log_info('aliyunpan checkin error' + str(e) + '    \n', my_logger=self.logger)
            self.checkin_message.append('main function: aliyunpan checkin error, the error is ' + str(e) + '    \n')
            log_info('*******************************aliyunpan error*******************************', my_logger=self.logger)
            return ''.join(self.checkin_message), False
