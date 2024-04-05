import json
import os
import time
from os import environ

import requests
from aligo import Aligo, Token, set_config_folder
from aligo.error import AligoRefreshFailed

from yaoys_checkin.aliyunpan_checkin.aliyunpan_task.aliyunpan_task import create_album, create_quick_pass, delete_deviceRoom_xuni_device, delete_file, delete_lastTime_album, delete_photo_from_album, device_room_task, fish_save, follow_user, get_device_room_info, \
    get_lucky_bittle, openAutoBackup_oneHour, \
    openAutoBackup_uploadFile, \
    play_video_by_mobile2, \
    share_sign_info, upload_file, \
    upload_photo
from yaoys_checkin.checkin_util import get_config_file
from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.checkin_util.logutil import log_info
from yaoys_checkin.model.all_class_parent import allClassParent


class aliyunpan(allClassParent):
    def __init__(self, **kwargs):
        super(aliyunpan, self).__init__(**kwargs)
        # access_token
        self.is_login = False
        self.session = None
        self.access_token = None
        self.expired_at = None
        self.phone = None
        self.account_checkin_message = ''

        # 配置文件夹路径 ./aliyunpan_config/
        # 如果是青龙面板
        if 'use_type' in self.config_file['common_config'] and self.config_file['common_config']['use_type'] == 0:
            self.aliyunpan_daily_task_folder = '/ql/data/aliyunpan_daily_task/'
            _config_path = os.path.join(os.getcwd(), '/ql/data/config')
            self.config_folder = os.path.normpath(_config_path)

        # 如果是Windows服务或者exe
        elif ('use_type' in self.config_file['common_config'] and self.config_file['common_config']['use_type'] == 1) or \
                ('use_type' in self.config_file['common_config'] and self.config_file['common_config']['use_type'] == 2):
            self.aliyunpan_daily_task_folder = '../aliyunpan_daily_task/'
            _config_path = os.path.join(os.getcwd(), '../config')
            self.config_folder = os.path.normpath(_config_path)
        else:
            log_info('use_type只能为0或者1', my_logger=self.logger)
            raise ValueError('use_type只能为0、1、2')

        if 'auto_delete_device' in self.config_file['cookieOrUser']['aliyunpan']:
            self.auto_delete_device = self.config_file['cookieOrUser']['aliyunpan']['auto_delete_device']
        else:
            self.auto_delete_device = False

        # 配置文件名
        self.account_config_name = ''

        # 登录成功后用户信息,包括access_token,username,等,详情查看aligo.Token类
        self.user_info = None
        # Aligo库对象，后续如果需要上传文件等需要使用
        self.aligo = None
        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])
        # 每日签到任务json
        self.daily_task_json = None

        # aligo设置配置文件路径
        set_config_folder(path=self.config_folder)

        # 开始签到
        self.checkin_message, self.is_success = self.aliyunpan_sign()
        # self.get_checkin_message()

    # 根据配置文件获取用户信息，如果配置文件不存在则重新登陆
    # def __get_user_config__(self):
    #     is_login = False
    #     try:
    #         # 判断配置文件是否存在，如果配置文件存在，则验证token是否有效，如果有效则不进行登录
    #         if os.path.exists(f'{self.config_folder + "/" + self.account_config_name}.json'):
    #             # 读取配置文件中的token等配置信息
    #             file = open(f'{self.config_folder + "/" + self.account_config_name}.json', encoding='utf-8')
    #             user_info = Token(**json.load(file))
    #             self.access_token = user_info.access_token
    #             is_valid = self.__check_token__()
    #             file.close()
    #             self.user_info = user_info
    #             # 配置文件有效，则不需要登录
    #             if is_valid is True:
    #                 self.user_info = user_info
    #                 self.aligo = Aligo(name=self.account_config_name, re_login=False, level=50, refresh_token=None)
    #                 is_login = True
    #                 self.access_token = self.user_info.access_token
    #             #     如何得到self.aligo
    #             else:
    #                 # 无效，需要重新登陆，则使用配置文件中最新的 refresh_token
    #                 self.refresh_token = user_info.refresh_token
    #                 is_login, self.user_info, self.aligo = self.__aliyunpan_login__()
    #                 self.access_token = self.user_info.access_token
    #         # 配置文件不存在，重新登录,此时使用用户配置的 refresh_token
    #         else:
    #             is_login, self.user_info, self.aligo = self.__aliyunpan_login__()
    #             if self.user_info is not None:
    #                 self.access_token = self.user_info.access_token
    #             else:
    #                 self.access_token = None
    #     except AligoRefreshFailed as e:
    #         log_info('refresh_token已失效，请更新refresh_token', my_logger=self.logger)
    #         is_login = False
    #         self.access_token = None
    #         self.account_checkin_message += 'refresh_token已失效，请更新refresh_token'
    #
    #     # 还是登录失败，说明无论是用户配置的还是文件中的全部失效，则需要提醒用户更新 refresh_token
    #     if is_login is False:
    #         self.account_checkin_message += 'refresh_token已失效，请更新refresh_token'
    #         log_info('refresh_token已失效，请更新refresh_token', my_logger=self.logger)
    #         self.user_info = None
    #         self.aligo = None
    #         self.access_token = None

    # 检查配置文件中的token是否有效
    # def __check_token__(self):
    #     if self.access_token is None:
    #         return False
    #     data = self.session.post(
    #         'https://api.aliyundrive.com/adrive/v1/user_config/get',
    #         headers={
    #             'Authorization': f'Bearer {self.access_token}'
    #         },
    #         json={},
    #     )
    #     if data.status_code == 200:
    #         json_data = data.json()
    #         if json_data is not None and 'user_id' in json_data and json_data['user_id'] is not None:
    #             return True
    #         else:
    #             return False
    #     else:
    #         return False

    # 登录
    def __aliyunpan_login__(self):
        if self.refresh_token is None:
            return False, None, None
        try:
            ali = Aligo(refresh_token=self.refresh_token, level=50, name=self.account_config_name, re_login=False)
            # 登陆成功，读取配置文件的信息
            if ali is not None and ali.user_id is not None:
                file = open(f'{self.config_folder + "/" + self.account_config_name}.json', encoding='utf-8')
                user_info = Token(**json.load(file))
                file.close()

                self.access_token = user_info.access_token
                return True, user_info, ali, self.access_token
            else:
                return False, None, None, None

        except AligoRefreshFailed as e:
            return False, None, None, None

    # 获取每日签到任务详情
    def get_daily_task_info(self, data):
        # dailyTask = ""
        is_getDailyTask = False

        # task_jiangli_name = ''
        task_remind = ''
        task_status = ''
        if 'signInInfos' in data['result'] and len(data['result']['signInInfos']) > 0:
            signInInfos_array = data['result']['signInInfos']
            # 遍历signInInfos
            for i in range(len(signInInfos_array)):
                # 得到最新签到的数据
                if data["result"]["signInCount"] == int(signInInfos_array[i]['day']):
                    # 遍历今日签到详情
                    if 'rewards' in signInInfos_array[i]:
                        for j in range(len(signInInfos_array[i]['rewards'])):
                            if 'type' in signInInfos_array[i]['rewards'][j] and 'name' in signInInfos_array[i]['rewards'][j] and 'remind' in signInInfos_array[i]['rewards'][j]:
                                # 如果是每日签到任务
                                if signInInfos_array[i]['rewards'][j]['type'] == 'dailyTask':
                                    # dailyTask = signInInfos_array[i]['rewards'][j]['name'] + ',领取条件: ' + signInInfos_array[i]['rewards'][j]['remind'] + ',请前往APP完成并领取奖励'
                                    # task_jiangli_name = signInInfos_array[i]['rewards'][j]['name']
                                    task_remind = signInInfos_array[i]['rewards'][j]['remind']
                                    task_status = signInInfos_array[i]['rewards'][j]['status']
                                    is_getDailyTask = True
                                    break
                            else:
                                continue
                if is_getDailyTask is True:
                    break
        return task_remind, task_status, is_getDailyTask

    # 新版签到获取每日签到任务
    def daily_sign_task(self, data):
        task_remind, task_status, is_getDailyTask = self.get_daily_task_info(data=data)
        task_reward_info = ''
        message = ''
        # 如果成功获取到了每日签到任务详情
        if is_getDailyTask:
            is_success = False
            device_id = None
            # 执行每日签到任务
            if self.daily_task_json is not None:
                try:
                    # 遍历配置文件中的每日签到任务，找到执行哪一个
                    for i in range(len(self.daily_task_json)):
                        # 相册上传十张照片
                        if self.daily_task_json[i]['remind'] == task_remind and self.daily_task_json[i]['type'] == 'photo':
                            # 删除相册内的图片
                            message, is_success = delete_photo_from_album(aligo=self.aligo, time_sleep=self.time_sleep)
                            # #     删除文件夹内的图片，因为上传图片时需要先上传至文件夹，在移动
                            # message, is_success = delete_file(aligo=self.aligo, time_sleep=self.time_sleep)
                            time.sleep(self.time_sleep)
                            message, is_success, albums_id = upload_photo(aligo=self.aligo, path=f'{self.aliyunpan_daily_task_folder}album', time_sleep=self.time_sleep)
                            break
                        # 订阅官方账号"阿里盘盘酱"
                        elif self.daily_task_json[i]['remind'] == task_remind and self.daily_task_json[i]['type'] == 'follow':
                            message, is_success = follow_user(access_token=self.access_token, session=self.session, time_sleep=self.time_sleep)
                            break
                        # 播放 30s 视频
                        elif self.daily_task_json[i]['remind'] == task_remind and self.daily_task_json[i]['type'] == 'video':
                            is_success, message = play_video_by_mobile2(aligo=self.aligo, access_token=self.access_token)
                            break
                        # 备份盘上传十个文件
                        elif self.daily_task_json[i]['remind'] == task_remind and self.daily_task_json[i]['type'] == 'file':
                            # 执行该任务前首先删除网盘内的所有文件
                            message, is_success = delete_file(aligo=self.aligo)
                            time.sleep(self.time_sleep)
                            # 上传文件
                            message, is_success = upload_file(aligo=self.aligo, path=f'{self.aliyunpan_daily_task_folder}file', time_sleep=self.time_sleep)
                            break
                        # 接3次好运瓶即可领取奖励
                        elif self.daily_task_json[i]['remind'] == task_remind and self.daily_task_json[i]['type'] == 'lucky':
                            message, is_success = get_lucky_bittle(access_token=self.access_token, session=self.session, time_sleep=self.time_sleep)
                            break
                        # 创建一个手工相册
                        elif self.daily_task_json[i]['remind'] == task_remind and self.daily_task_json[i]['type'] == 'album':
                            # 删除上次创建的相册
                            is_success, message = delete_lastTime_album(aligo=self.aligo)
                            time.sleep(self.time_sleep)
                            # 创建相册
                            album_id, is_success = create_album(aligo=self.aligo, path=f'{self.aliyunpan_daily_task_folder}album', time_sleep=self.time_sleep, album_type=1)
                            break
                        # 快传功能传输文件
                        elif self.daily_task_json[i]['remind'] == task_remind and self.daily_task_json[i]['type'] == 'quick_pass':
                            is_success, message = create_quick_pass(aligo=self.aligo, access_token=self.access_token)
                            break
                        # 分享好运卡
                        elif self.daily_task_json[i]['remind'] == task_remind and self.daily_task_json[i]['type'] == 'share_sign':
                            is_success, message = share_sign_info(access_token=self.access_token)
                            break
                        # 捞取好运瓶并保存任意一个文件
                        elif self.daily_task_json[i]['remind'] == task_remind and self.daily_task_json[i]['type'] == 'fish_save':
                            is_success, message = fish_save(aligo=self.aligo, access_token=self.access_token, time_sleep=self.time_sleep)
                            break

                        # 开启自动备份并备份满10个文件
                        elif self.daily_task_json[i]['remind'] == task_remind and self.daily_task_json[i]['type'] == 'auto_backup_upload_file':
                            is_success = False
                            message = '暂不支持该任务'
                            # is_success, message, device_id = openAutoBackup_uploadFile(aligo=self.aligo, access_token=self.access_token, time_sleep=self.time_sleep, file_num=10, refreshToken=self.refresh_token, logger=self.logger)
                            break

                        # 开启手机自动备份并持续至少一小时
                        elif task_remind in self.daily_task_json[i]['remind'] and self.daily_task_json[i]['type'] == 'auto_backup_one_hour':
                            is_success = False
                            message = '暂不支持该任务'
                            # is_success, message, device_id = openAutoBackup_oneHour(aligo=self.aligo, access_token=self.access_token, time_sleep=self.time_sleep)
                            break
                        else:
                            message = f'配置文件不包含该任务或不支持该任务'
                            is_success = False
                except Exception as e:
                    log_info('执行每日签到任务异常:' + str(e), my_logger=self.logger)
                    return '执行每日签到任务异常:' + str(e)
            # 每日任务已完成，执行任务签到
            if is_success is True:
                # 任务完成后再次请求签到列表
                time.sleep(self.time_sleep)

                if device_id is None:
                    sign_headers = {
                        'Authorization': f'Bearer {self.access_token}',
                    }
                else:
                    sign_headers = {
                        'Authorization': f'Bearer {self.access_token}',
                        'x-device-id': device_id
                    }

                data = self.session.post(
                    'https://member.aliyundrive.com/v2/activity/sign_in_list?_rx-s=mobile',
                    headers=sign_headers,
                    json={},
                ).json()
                task_remind, task_status, is_getDailyTask = self.get_daily_task_info(data=data)
                if task_status == 'verification':
                    return '每日签到任务奖励已经领取'
                if task_status == 'finished':
                    # 执行签到
                    reward_data = self.session.post(
                        'https://member.aliyundrive.com/v2/activity/sign_in_task_reward?_rx-s=mobile',
                        # params={'_rx-s': 'mobile'},
                        headers=sign_headers,
                        json={'signInDay': data['result']['signInCount']},
                    ).json()
                    if 'success' in reward_data:
                        task_reward_info = '每日签到任务奖励名称:' + reward_data['result']['name'] + ' ' + reward_data['result']['notice']
                    else:
                        task_reward_info = reward_data['message']
                else:
                    task_reward_info = '每日签到任务未完成，请手动完成任务'
            else:
                log_info(message, my_logger=self.logger)
                task_reward_info = f'每日签到任务执行失败,失败原因:{message}，请手动执行'
        else:
            task_reward_info = f'每日签到任务执行失败,失败原因:{message}，请手动执行'

        return task_reward_info

    # 签到
    def sign_in(self):
        try:
            # 1. 执行登录签到并领取奖励
            is_checkin = True
            data = self.session.post(
                'https://member.aliyundrive.com/v2/activity/sign_in_list?_rx-s=mobile',
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                },
                json={},
            ).json()
            if 'success' not in data:
                # log_info(f'[{phone}] 签到失败, 错误信息: {data}', my_logger=checkin_logger)
                self.account_checkin_message += f'[{self.user_info.user_name}] 签到失败, 错误信息: {data}\n'
                is_checkin = False
            # 登录签到成功后领取奖励
            if is_checkin is True and 'result' in data and isinstance(data['result'], dict) is True:
                time.sleep(self.time_sleep)
                # 获取已签到总数
                signCount = data['result']['signInCount']
                # 获取今日签到状态
                sign_status = data['result']['signInInfos'][signCount - 1]['status']
                # 已经签到过，不再重复签到
                if sign_status == 'normal':
                    self.account_checkin_message += f'{self.user_info.user_name} 今日已签到 '
                    # return True
                # 领取奖励
                reward_data = self.session.post(
                    'https://member.aliyundrive.com/v1/activity/sign_in_reward?_rx-s=mobile',
                    params={'_rx-s': 'mobile'},
                    headers={'Authorization': f'Bearer {self.access_token}'},
                    json={'signInDay': data['result']['signInCount']},
                ).json()

                reward = (
                    '无奖励'
                    if not reward_data['success'] or reward_data is None
                    else f'获得{reward_data["result"]["name"]},{reward_data["result"]["notice"]}'
                )

                self.account_checkin_message += f'[{self.user_info.user_name}] 签到成功, 本月累计签到 {data["result"]["signInCount"]} 天.'
                self.account_checkin_message += f' 本次签到奖励: {reward}'

            # 2. 执行签到任务并领取奖励
            task_reward_info = self.daily_sign_task(data=data)
            if task_reward_info != "":
                self.account_checkin_message += f'. 签到任务: {task_reward_info}'

            # 3. 执行时光设备间任务
            if "deviceRoom_task" in self.config_file['cookieOrUser']["aliyunpan"] and self.config_file['cookieOrUser']["aliyunpan"]['deviceRoom_task'] is True:
                has_device_room, info = get_device_room_info(access_token=self.access_token)
                if has_device_room:
                    is_success, device_room_task_info = device_room_task(aligo=self.aligo,
                                                                         access_token=self.access_token,
                                                                         time_sleep=self.time_sleep,
                                                                         refresh_token=self.refresh_token,
                                                                         auto_delete_device=self.auto_delete_device,
                                                                         logger=self.logger)
                    if is_success:
                        self.account_checkin_message += f', 时光设备间任务执行成功: {device_room_task_info}'
                    else:
                        self.account_checkin_message += f', 时光设备间任务失败: {device_room_task_info}'

                    if self.auto_delete_device is True:
                        delete_deviceRoom_message = delete_deviceRoom_xuni_device(access_token=self.access_token)
                        self.account_checkin_message += ', ' + delete_deviceRoom_message
            return True
        except Exception as e:
            log_info('阿里云盘签到错误，' + str(e), my_logger=self.logger)
            self.account_checkin_message += '阿里云盘签到错误，' + str(e)

        return False

    def aliyun_checkin(self):

        self.account_checkin_message = ''
        self.account_checkin_message += f"[阿里云盘账号_{self.account_index}]:"
        self.is_login = False
        if self.refresh_token is not None and len(self.refresh_token) > 0:
            self.session = requests.sessions.session()
            environ['NO_PROXY'] = '*'  # 禁止代理
            # # 设置aligo请求头
            # UNI_HEADERS.update({
            #     'User-Agent': 'AliApp(AYSD/4.9.3) com.alicloud.smartdrive/4.9.3 Version/16.6 Channel/201200 Language/zh-Hans-CN /iOS Mobile/iPhone14,5',
            # })
            # 获取token，每次签到都重新登录
            # self.__get_user_config__()
            self.is_login, self.user_info, self.aligo, self.access_token = self.__aliyunpan_login__()
            if self.access_token is None and self.is_login is False:
                # 说明token失效，则删除生成的配置文件
                if os.path.exists(f'{self.config_folder + "/" + self.account_config_name}.json') is True:
                    os.remove(f'{self.config_folder + "/" + self.account_config_name}.json')
                self.account_checkin_message += 'refresh_token失效，请更新refresh_token'
                return self.account_checkin_message

            time.sleep(self.time_sleep)
            # 签到
            if self.sign_in() is False:
                self.account_checkin_message += f'[{self.user_info.user_name}] 签到失败.'
                log_info(f'[{self.user_info.user_name}] 签到失败.', my_logger=self.logger)
        else:
            self.account_checkin_message += 'refresh_tokens 不能为空'

        # 账号签到完毕后删除配置文件
        if os.path.exists(f'{self.config_folder + "/" + self.account_config_name}.json') is True:
            os.remove(f'{self.config_folder + "/" + self.account_config_name}.json')

        self.account_checkin_message += '       \n'
        return self.account_checkin_message

    def aliyunpan_sign(self):
        if self.checkin_verification is None or self.checkin_verification == '':
            return ''.join(self.checkin_message), False

        try:
            # 读取配置文件中的每日签到任务
            self.daily_task_json = get_config_file(config_type=1)
            log_info('**********************************aliyunpan checkin***************************************', my_logger=self.logger)
            if self.checkin_verification is not None and len(self.checkin_verification) > 0:
                if isinstance(self.checkin_verification, str) is True:
                    self.refresh_token = self.checkin_verification
                    self.account_index = 1
                    self.account_config_name = '阿里云盘账号_' + str(self.account_index)
                    self.checkin_message.append(self.aliyun_checkin())
                elif isinstance(self.checkin_verification, list) is True:
                    for i in range(0, len(self.checkin_verification)):
                        if isinstance(self.checkin_verification[i], dict) is True:
                            self.refresh_token = self.checkin_verification[i]['cookie']
                            self.account_index = i + 1
                            self.account_config_name = '阿里云盘账号_' + str(self.account_index)
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
