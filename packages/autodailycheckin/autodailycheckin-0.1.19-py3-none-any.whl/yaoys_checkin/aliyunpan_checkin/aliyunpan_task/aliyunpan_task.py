# -*- coding: utf-8 -*-
# @FileName  :album_task.py
# @Time      :2023/8/7 21:51
# @Author    :yaoys
# @Desc      : 阿里云盘相册相关的任务
import datetime
import json
import os
import random
import time
from urllib.parse import urlparse

import m3u8
import requests
from PIL import Image

from yaoys_checkin.aliyunpan_checkin.aliyunpan_task.alipan_utils import create_device_session, random_hex, device_logout
from yaoys_checkin.checkin_util.logutil import log_info

# 上传文件名前缀
file_name_prex = '阿里云盘上传文件_'
# 上传文件夹名称
folder_name = '阿里云盘签到任务文件夹'
video_folder_name = 'video'
# 上传图片相册
upload_photo_album_name = '阿里云盘签到任务相册'
# 阿里盘酱酱ID
alipanpanjiang_id = 'ec11691148db442aa7aa374ca707543c'
# 创建手工相册名前缀，格式为'阿里云盘签到任务创建相册_'+当前日期
create_album_name = '阿里云盘签到任务创建相册'

video_file_type = ["avi", "flv", "mp4", "MOV"]

device_type_Android = 'Android'
device_type_iOS = 'iOS'

# 时光设备间任务虚拟设备
moni_deviceName = 'XuNi_XiaoMi 14Pro'
moni_modelName = 'XuNi_xiaomi'
android_x_canary = 'client=Android,app=adrive,version=v5.4.1'
android_user_agent = 'AliApp(AYSD/5.4.1) com.alicloud.databox/34760760 Channel/36176727979800@rimet_android_5.4.1 language/zh-CN /Android Mobile/Mi 6X'
ios_x_canary = 'client=iOS,app=adrive,version=v5.4.1'
ios_user_agent = 'AliApp(AYSD/5.4.1) com.alicloud.smartdrive/5.4.1 Version/16.7.2 Channel/201200 Language/zh-Hans-CN /iOS Mobile/iPhone14,5'
windows_x_canary = 'client=windows,app=adrive,version=v4.12.0'
windows_user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) aDrive/4.12.0 Chrome/108.0.5359.215 Electron/22.3.24 Safari/537.36'
x_canary = ios_x_canary
user_agent = ios_user_agent


def openAutoBackup_oneHour(aligo=None, access_token=None, time_sleep=0):
    if access_token is None:
        return False, 'access_token为空'
    if aligo is None:
        return False, 'aligo为空'

    # 获取账号的所有设备，并获取安卓或者苹果手机的设备ID
    device_info = requests.post(url='https://user.aliyundrive.com/v1/deviceRoom/listDevice', headers={
        'Authorization': f'Bearer {access_token}'}).json()
    if "items" not in device_info:
        return False, "获 取设备信息错误"
    for i in range(0, len(device_info['items'])):
        device_id = device_info['items'][i]['id']
        # 获取该设备的详细信息
        device_summary = requests.post(url='https://api.alipan.com/adrive/v2/backup/device_summary',
                                       json={"deviceId": device_id},
                                       headers={'Authorization': f'Bearer {access_token}', 'x-device-id': device_id}
                                       ).json()
        autoStatus = device_summary['albumBackupSetting']['autoStatus']
        enable = device_summary['enable']
        time.sleep(2)
        if autoStatus is True and enable is True:
            result = requests.post(url='https://api.aliyundrive.com/users/v1/users/update_device_extras',
                                   headers={'Authorization': f'Bearer {access_token}', 'x-device-id': device_id},
                                   json={"autoBackupStatus": True}
                                   ).json()
            if 'result' in result and result['result'] is True:
                return True, "执行自动备份任务成功", device_id
    return False, '开启自动备份设备失败', None


# 开启手机自动备份并备份一定数量的文件，只支持安卓和苹果
def openAutoBackup_uploadFile(aligo=None, access_token=None, time_sleep=0, file_num=0, refreshToken=None, logger=None):
    if access_token is None:
        return False, 'access_token为空'
    if aligo is None:
        return False, 'aligo为空'
    android_x_canary = 'client=Android,app=adrive,version=v5.4.1'
    android_user_agent = 'AliApp(AYSD/5.4.1) com.alicloud.databox/34760760 Channel/36176727979800@rimet_android_5.4.1 language/zh-CN /Android Mobile/Mi 6X'

    moni_deviceName = 'XiaoMi 14Pro'
    moni_modelName = 'xiaomi'
    deviceId = random_hex(64)
    pubKey = random_hex(32)

    # 上报备份
    requests.post(f'https://api.alipan.com/users/v1/users/update_device_extras',
                  headers={
                      'Authorization': f'Bearer {access_token}',
                      "x-device-id": deviceId
                  },
                  json={
                      'albumAccessAuthority': True,
                      'albumBackupLeftFileTotal': 0,
                      'albumBackupLeftFileTotalSize': 0,
                      'albumFile': 0,
                      'autoBackupStatus': True,
                      'brand': moni_modelName,
                      'systemVersion': 'Android 13',
                  })
    time.sleep(2)

    # 创建虚拟设备
    result = create_device_session(
        user_id=aligo.get_user().user_id,
        accesstoken=access_token,
        deviceId=deviceId,
        signature=None,
        refreshToken=refreshToken,
        pubKey=pubKey,
        deviceName=moni_deviceName,
        modelName=moni_modelName,
        x_canary=android_x_canary,
        user_agent=android_user_agent,
        logger=logger
    )
    if result[0] is False:
        return False, "创建虚拟设备失败"

    signature = result[1]['signature']

    if file_num > 0:
        # 上传固定数量的文件
        # 使用不同的device上传一张照片
        aligo._auth.session.headers["x-device-id"] = deviceId
        upload_file(aligo=aligo, path='../aliyunpan_daily_task/file', time_sleep=2, file_num=file_num)

    time.sleep(2)
    # 创建虚拟设备
    result = create_device_session(
        user_id=aligo.get_user().user_id,
        accesstoken=access_token,
        deviceId=deviceId,
        signature=signature,
        refreshToken=refreshToken,
        pubKey=pubKey,
        deviceName=moni_deviceName,
        modelName=moni_modelName,
        x_canary=android_x_canary,
        user_agent=android_user_agent,
        logger=logger
    )
    time.sleep(2)
    # 上报备份
    requests.post(f'https://api.alipan.com/users/v1/users/update_device_extras',
                  headers={
                      'Authorization': f'Bearer {access_token}',
                      "x-device-id": deviceId
                  },
                  json={
                      'albumAccessAuthority': True,
                      'albumBackupLeftFileTotal': 0,
                      'albumBackupLeftFileTotalSize': 0,
                      'albumFile': 0,
                      'autoBackupStatus': True,
                      'brand': moni_modelName,
                      'systemVersion': 'Android 13',
                  })
    # time.sleep(5)
    # #     领取成功退出登陆
    # device_logout(deviceId, access_token)
    # #     从时光设备间删除设备
    # time.sleep(5)
    # requests.post(
    #     url='https://api.alipan.com/users/v1/users/remove_device_backup_list',
    #     headers={
    #         'Authorization': f'Bearer {access_token}',
    #         'x-signature': signature
    #     },
    #     json={
    #         "deviceId": deviceId
    #     }
    # )
    return True, "已开启自动备份并备份满10个文件", deviceId


# 接一个好运瓶并保存其中的文件
def fish_save(access_token=None, time_sleep=0, aligo=None):
    if access_token is None:
        return False, 'access_token为空'

    # 获取账号的所有设备，并获取安卓或者苹果手机的设备ID
    device_info = requests.post(url='https://user.aliyundrive.com/v1/deviceRoom/listDevice', headers={
        'Authorization': f'Bearer {access_token}'}).json()
    if "items" not in device_info:
        return False, "获取设备信息错误"

    device_id = None
    for i in range(0, len(device_info['items'])):
        if device_info['items'][i]['deviceNameInfo']['deviceType'] != device_type_Android \
                and device_info['items'][i]['deviceNameInfo']['deviceType'] != device_type_iOS:
            continue

        device_id = device_info['items'][i]['id']
        break

    # 获取用户默认保存的目录,默认为资源库中的来自分享目录
    resource_drive_id = get_user_drive_id(aligo=aligo, category='resource')
    if resource_drive_id is None or len(resource_drive_id) != 2 or resource_drive_id[0] is None:
        return False, "获取资源库ID失败"
    resource_drive_id = resource_drive_id[0]

    fishBottleLimit = 3
    # 获取用户捞取好运瓶上限和今日已使用
    user_limit = requests.post("https://api.alipan.com/adrive/v1/bottle/getUserLimit", headers={
        'Authorization': f'Bearer {access_token}'}, json={}).json()

    if "fishBottleLimit" in user_limit:
        fishBottleLimit = user_limit['fishBottleLimit']

    if "fishBottleUsed" in user_limit:
        fishBottleUsed = user_limit['fishBottleUsed']
        if fishBottleUsed >= fishBottleLimit:
            return False, "今日捞取好运瓶已经达到上限，请明日重试"
    # 捞取好运瓶获取分享ID
    fish_info = requests.post('https://api.alipan.com/adrive/v1/bottle/fish', headers={
        'Authorization': f'Bearer {access_token}'}, json={}).json()

    shareId = None
    if "shareId" in fish_info:
        shareId = fish_info['shareId']

    if shareId is None:
        return False, "获取分享ID失败"

    # 根据shareId获取shareToken，并添加至header中
    shareToken_info = requests.post('https://api.alipan.com/v2/share_link/get_share_token', headers={
        'Authorization': f'Bearer {access_token}'}, json={
        "share_id": shareId
    }).json()
    if "share_token" not in shareToken_info:
        return False, "获取 share_token 失败"
    shareToken = shareToken_info['share_token']

    default_save_location = requests.post(url='https://api.alipan.com/adrive/v1/user_config/get_default_save_location',
                                          headers={
                                              'Authorization': f'Bearer {access_token}',
                                              'x-device-id': device_id
                                          },
                                          json={
                                              "drive_id": resource_drive_id
                                          }).json()

    # 判断捞到的好运瓶的文件数量
    share_file_count_info = requests.post(url='https://api.alipan.com/adrive/v2/share_link/get_share_by_anonymous',
                                          headers={
                                              'Authorization': f'Bearer {access_token}',
                                              "x-share-token": shareToken
                                          },
                                          json={
                                              "share_id": shareId
                                          }).json()

    share_file_count = share_file_count_info['file_count']
    # 如果分享的为多个文件，则选择其中一个进行保存
    # 获取到分享的文件夹中的所有的文件，并选择一个进行保存
    share_file_info = requests.post("https://api.alipan.com/adrive/v2/file/list_by_share",
                                    headers={
                                        'Authorization': f'Bearer {access_token}',
                                        "x-share-token": shareToken
                                    },
                                    json={
                                        "fields": "*",
                                        "office_thumbnail_process": "image/resize,m_lfit,w_256,limit_0/format,avif",
                                        "image_thumbnail_process": "image/resize,m_lfit,w_256,limit_0/format,avif",
                                        "order_direction": "DESC",
                                        "share_id": shareId,
                                        "order_by": "name",
                                        "limit": 50,
                                        "video_thumbnail_process": "video/snapshot,t_120000,f_jpg,m_lfit,w_256,ar_auto,m_fast",
                                        "parent_file_id": "root",
                                        "all": False
                                    }).json()

    # 选择一个文件进行保存
    save_batch = requests.post('https://api.alipan.com/adrive/v2/batch',
                               headers={
                                   'Authorization': f'Bearer {access_token}',
                                   "x-share-token": shareToken
                               },
                               json={
                                   "requests": [{
                                       "body": {
                                           # 源文件网盘ID
                                           "drive_id": share_file_info['items'][0]['drive_id'],
                                           # 目标网盘ID
                                           "to_drive_id": resource_drive_id,
                                           # 目标网盘文件夹ID
                                           "to_parent_file_id": default_save_location['file_id'],
                                           # 源文件ID
                                           "file_id": share_file_info['items'][0]['file_id'],
                                           "auto_rename": True,
                                           "share_id": shareId
                                       },
                                       "id": "0",
                                       "method": "POST",
                                       "url": "/file/copy"
                                   }],
                                   "resource": "file"
                               }).json()

    if save_batch['responses'][0]['body']['drive_id'] != resource_drive_id:
        return False, "保存好运瓶文件失败"
    #     保存好运瓶中的内容
    save_info = requests.post("https://api.alipan.com/v2/report_event",
                              headers={
                                  'Authorization': f'Bearer {access_token}',
                                  "x-share-token": shareToken
                              },
                              json={
                                  "share_link": {
                                      "share_id": shareId,
                                      "sub_type": "save"
                                  },
                                  "event_type": "share_link"
                              }).json()
    return True, "保存好运瓶内容成功"


# 分享好运卡
def share_sign_info(access_token=None):
    if access_token is None:
        return False, 'access_token为空'

    share_signInfo = requests.post("https://member.aliyundrive.com/v1/activity/behave?_rx-s=mobile", headers={
        'Authorization': f'Bearer {access_token}'}, json={
        "behave": "share-signIn-code"
    }).json()

    if "success" in share_signInfo and share_signInfo['success'] is True:
        return True, "分享好运卡成功"
    else:
        return False, "分享好运卡成功"


def get_device_room_info(access_token=None):
    if access_token is None:
        return False, 'access_token为空'

    device_info = requests.post("https://api.alipan.com/apps/v2/users/home/widgets", headers={
        'Authorization': f'Bearer {access_token}'}, json={}).json()

    if "minorBackup" in device_info:
        return True, "获取时光设备间成功"
    else:
        return False, "时光设备间不存在"


def device_room_task(aligo=None, access_token=None, time_sleep=0, refresh_token=None, auto_delete_device=False, logger=None):
    if aligo is None:
        return False, 'aligo 为空'

    if access_token is None:
        return False, 'access_token为空'

    if refresh_token is None:
        return False, 'refresh_token为空'

    if logger is None:
        return False, 'logger为空'

    try:
        # log_info('获取今日领取次数', my_logger=logger)
        # 今日领取次数
        rewardCountToday = 0
        reward_info = requests.post("https://member.aliyundrive.com/v1/deviceRoom/rewardInfoToday", headers={
            'Authorization': f'Bearer {access_token}'}).json()
        if 'success' in reward_info and 'result' in reward_info and 'rewardCountToday' in reward_info['result']:
            rewardCountToday = reward_info['result']['rewardCountToday']
            if rewardCountToday >= 5:
                return True, "已经领取过5次了,无法重复领取"
            time.sleep(2)
        else:
            return False, '获取今日领取次数失败'

        # 定义一个时光设备间中用户自己的设备id，使用该id删除创建的虚拟设备，虚拟设备删除时不能使用要删除的设备id，即不能自己删除自己
        user_device_id = None
        device_room_device_info = requests.post(url='https://user.aliyundrive.com/v1/deviceRoom/listDevice',
                                                headers={
                                                    'Authorization': f'Bearer {access_token}'}
                                                ).json()

        if 'items' not in device_room_device_info:
            return False, '获取时光设备间设备信息失败'
        # 使用自己的设备执行时光设备间任务
        # log_info('使用原有设备执行任务', my_logger=logger)
        if len(device_room_device_info['items']) > 0:
            for j in range(0, len(device_room_device_info['items'])):
                if device_room_device_info['items'][j]['deviceNameInfo']['deviceType'].lower() == 'Android'.lower():
                    x_canary = android_x_canary
                    user_agent = android_user_agent
                elif device_room_device_info['items'][j]['deviceNameInfo']['deviceType'].lower() == 'IOS'.lower():
                    x_canary = ios_x_canary
                    user_agent = ios_user_agent
                elif device_room_device_info['items'][j]['deviceNameInfo']['deviceType'].lower() == 'Windows'.lower():
                    x_canary = windows_x_canary
                    user_agent = windows_user_agent
                else:
                    return False, '请求头错误,请手动执行'

                if user_device_id is None:
                    user_device_id = device_room_device_info['items'][j]['id']

                aligo._auth.session.headers["x-device-id"] = device_room_device_info['items'][j]['id']
                # 上传一个文件
                upload_file(aligo=aligo, path='../aliyunpan_daily_task/file', file_num=1)
                time.sleep(3)

                pubkey = random_hex(32)
                signature = None

                result = create_device_session(
                    user_id=aligo.get_user().user_id,
                    accesstoken=access_token,
                    deviceId=device_room_device_info['items'][j]['id'],
                    signature=signature,
                    refreshToken=refresh_token,
                    pubKey=pubkey,
                    deviceName=device_room_device_info['items'][j]['deviceNameInfo']['deviceName'],
                    modelName=device_room_device_info['items'][j]['deviceNameInfo']['deviceModel'],
                    x_canary=x_canary,
                    user_agent=user_agent,
                    logger=logger
                )
                if result[0] is False:
                    log_info('create_device_session方法执行失败:' + result[1], my_logger=logger)
                    continue
                signature = result[1]['signature']
                time.sleep(2)
                # 上报备份
                requests.post(f'https://api.alipan.com/users/v1/users/update_device_extras',
                              headers={
                                  'Authorization': f'Bearer {access_token}',
                                  "x-device-id": device_room_device_info['items'][j]['id']
                              },
                              json={
                                  'albumAccessAuthority': True,
                                  'albumBackupLeftFileTotal': 0,
                                  'albumBackupLeftFileTotalSize': 0,
                                  'albumFile': 0,
                                  # 'autoBackupStatus': False,
                                  'brand': device_room_device_info['items'][j]['deviceNameInfo']['deviceModel'],
                                  'systemVersion': device_room_device_info['items'][j]['deviceNameInfo']['deviceType'],
                              })
                time.sleep(2)
                create_device_session(
                    user_id=aligo.get_user().user_id,
                    accesstoken=access_token,
                    deviceId=device_room_device_info['items'][j]['id'],
                    signature=signature,
                    refreshToken=refresh_token,
                    pubKey=pubkey,
                    deviceName=device_room_device_info['items'][j]['deviceNameInfo']['deviceName'],
                    modelName=device_room_device_info['items'][j]['deviceNameInfo']['deviceModel'],
                    x_canary=x_canary,
                    user_agent=user_agent,
                    logger=logger
                )
                time.sleep(2)
                requests.post(url='https://user.aliyundrive.com/v1/deviceRoom/listDevice',
                              headers={
                                  'Authorization': f'Bearer {access_token}',
                                  "x-device-id": device_room_device_info['items'][j]['id']
                              },
                              )
        time.sleep(5)
        # log_info('时光设备间任务出现异常，请查看日志222', my_logger=logger)
        # 用户自己的设备上传文件后领取奖励
        # log_info('领取奖励', my_logger=logger)
        device_room_device_info = requests.post(url='https://user.aliyundrive.com/v1/deviceRoom/listDevice', headers={
            'Authorization': f'Bearer {access_token}'}).json()
        if 'items' not in device_room_device_info:
            return False, '获取时光设备间设备信息失败'
        size_count = 0
        if len(device_room_device_info['items']) > 0:
            for j in range(0, len(device_room_device_info['items'])):
                if device_room_device_info['items'][j]['canCollectEnergy'] is True:
                    # 成功后领取奖励
                    reward_get_info = requests.post(url="https://member.aliyundrive.com/v1/deviceRoom/rewardEnergy", headers={
                        'Authorization': f'Bearer {access_token}'}, json={
                        "deviceId": device_room_device_info['items'][j]['id']
                    }).json()
                    if "success" in reward_get_info:
                        size_count += reward_get_info['result']['size']
                    else:
                        size_count += 0
                    time.sleep(2)

        # 今日领取次数
        # log_info('重新获取今日领取次数', my_logger=logger)
        reward_info = requests.post("https://member.aliyundrive.com/v1/deviceRoom/rewardInfoToday", headers={
            'Authorization': f'Bearer {access_token}'}).json()
        if 'success' in reward_info and 'result' in reward_info and 'rewardCountToday' in reward_info['result']:
            rewardCountToday = reward_info['result']['rewardCountToday']
            if rewardCountToday >= 5:
                return True, f"今日已领取{rewardCountToday}次，今日已获得{size_count}MB "
        else:
            return False, '获取今日领取次数失败'

        # 领取不足5次，创建虚拟设备领取
        # log_info('创建虚拟设备执行任务', my_logger=logger)
        while rewardCountToday < 5:
            deviceId = random_hex(64)
            pubKey = random_hex(32)
            signature = None
            # 创建虚拟设备
            result = create_device_session(
                user_id=aligo.get_user().user_id,
                accesstoken=access_token,
                deviceId=deviceId,
                signature=signature,
                refreshToken=refresh_token,
                pubKey=pubKey,
                deviceName=moni_deviceName,
                modelName=moni_modelName,
                x_canary=android_x_canary,
                user_agent=android_user_agent,
                logger=logger
            )
            if result[0] is False:
                return False, f"已经领取{rewardCountToday}次,余下次数创建虚拟设备失败,需要手动领取:" + result[1]

            signature = result[1]['signature']
            time.sleep(2)
            # 上报备份
            requests.post(f'https://api.alipan.com/users/v1/users/update_device_extras',
                          headers={
                              'Authorization': f'Bearer {access_token}',
                              "x-device-id": deviceId
                          },
                          json={
                              'albumAccessAuthority': True,
                              'albumBackupLeftFileTotal': 0,
                              'albumBackupLeftFileTotalSize': 0,
                              'albumFile': 0,
                              'autoBackupStatus': True,
                              'brand': moni_modelName,
                              'systemVersion': 'Android 13',
                          })
            time.sleep(2)
            # 使用不同的device上传一张照片
            aligo._auth.session.headers["x-device-id"] = deviceId
            # 上传一个文件
            upload_file(aligo=aligo, path='../aliyunpan_daily_task/file', file_num=1)
            time.sleep(3)
            # 再次使用刚才创建的虚拟设备访问
            create_device_session(
                user_id=aligo.get_user().user_id,
                accesstoken=access_token,
                deviceId=deviceId,
                signature=signature,
                refreshToken=refresh_token,
                pubKey=pubKey,
                deviceName=moni_deviceName,
                modelName=moni_modelName,
                x_canary=android_x_canary,
                user_agent=android_user_agent,
                logger=logger
            )
            time.sleep(3)
            requests.post(url='https://user.aliyundrive.com/v1/deviceRoom/listDevice', headers={
                'Authorization': f'Bearer {access_token}'}).json()
            time.sleep(2)
            reward_get_info = requests.post(url="https://member.aliyundrive.com/v1/deviceRoom/rewardEnergy", headers={
                'Authorization': f'Bearer {access_token}'}, json={
                "deviceId": deviceId
            }).json()
            if "success" in reward_get_info:
                size_count += reward_get_info['result']['size']
            else:
                size_count += 0

            reward_info = requests.post("https://member.aliyundrive.com/v1/deviceRoom/rewardInfoToday", headers={
                'Authorization': f'Bearer {access_token}'}).json()
            if 'result' not in reward_info or 'rewardCountToday' not in reward_info['result']:
                return False, "获取今日领取信息错误"
            rewardCountToday = reward_info['result']['rewardCountToday']
            if rewardCountToday >= 5:
                return True, f"今日已领取{rewardCountToday}次，今日已获得{size_count}MB "
            time.sleep(5)
            # log_info('时光设备间任务出现异常，请查看日志666', my_logger=logger)
    except Exception as e:
        log_info('时光设备间任务出现异常，请查看日志' + str(e), my_logger=logger)
        return False, f'时光设备间任务出现异常，请查看日志: {e}'


def delete_deviceRoom_xuni_device(access_token=None, time_sleep=0, refresh_token=None):
    device_room_device_info = requests.post(url='https://user.aliyundrive.com/v1/deviceRoom/listDevice',
                                            headers={
                                                'Authorization': f'Bearer {access_token}'}
                                            ).json()
    if 'items' not in device_room_device_info:
        return False, '删除虚拟设备时获取时光设备间设备信息失败'

    user_device_id = None
    delete_deviceRoom_message = ''

    if len(device_room_device_info['items']) > 0:
        for i in range(0, len(device_room_device_info['items'])):
            if moni_deviceName != device_room_device_info['items'][i]['deviceNameInfo']['deviceName']:

                if 'Android'.lower() == device_room_device_info['items'][i]['deviceNameInfo']['deviceType'].lower() \
                        or 'IOS'.lower() == device_room_device_info['items'][i]['deviceNameInfo']['deviceType'].lower():
                    user_device_id = device_room_device_info['items'][i]['id']

                continue

            if user_device_id is None:
                user_device_id = random_hex(32)

            device_id = device_room_device_info['items'][i]['id']
            #     从时光设备间删除设备
            result = requests.post(
                url='https://api.alipan.com/users/v1/users/remove_device_backup_list',
                headers={
                    'content-type': 'application/json;charset=UTF-8',
                    'Authorization': f'Bearer {access_token}',
                    'x-canary': android_x_canary,
                    'user-agent': android_user_agent,
                    "x-device-id": user_device_id
                },
                json={
                    "deviceId": device_id
                }
            ).json()
            time.sleep(2)
            if 'result' in result and 'success' in result and result['result'] is True and result['success'] is True:
                delete_deviceRoom_message = '已经删除创建的虚拟设备并在虚拟设备中退出登录'
            else:
                delete_deviceRoom_message = '删除时光设备间失败,请手动删除，避免影响下次执行该任务'

            # 领取成功退出登陆
            device_logout(device_id, access_token)
            time.sleep(2)
    return delete_deviceRoom_message


# 由于每个账号中drive_name名称不一致，比如有的账号备份盘drive_name叫做‘backup’，有的叫做Default，所以优先使用category进行匹配，如果category为空则使用drive_name
def get_user_drive_id(aligo=None, drive_name=None, category=None):
    if aligo is None:
        return None, 'aligo 为空'

    list_drive = aligo.list_my_drives()
    for i in range(len(list_drive)):
        if list_drive[i].drive_name is None:
            continue
        #    category不是空，优先使用
        if category is not None and len(category) > 0:
            if list_drive[i].drive_type == 'normal' and list_drive[i].status == 'enabled' and list_drive[i].category == category:
                return list_drive[i].drive_id, ''
        # 匹配相册时，由于category为空，所以使用名字
        else:
            if list_drive[i].drive_type == 'normal' and list_drive[i].status == 'enabled' and list_drive[i].drive_name == drive_name:
                return list_drive[i].drive_id, ''

    return None, '没有找到相应的drive'


# 创建快传分享文件夹,首先获取所有文档，然后随机选择一个文档创建快传
def create_quick_pass(aligo=None, access_token=None):
    if aligo is None:
        return False, 'aligo 为空'

    if access_token is None:
        return False, 'access_token为空'
    #     获取阿里云盘签到任务文件夹的id
    # 创建文件夹前首先获取备份盘的drive_id
    backup_drive_id = get_user_drive_id(aligo=aligo, category='backup')
    if backup_drive_id is None or len(backup_drive_id) != 2 or backup_drive_id[0] is None:
        return False, f'获取 备份盘ID失败'

    # 首先获取资源盘的drive_id
    resource_drive_id = get_user_drive_id(aligo=aligo, category='resource')
    if resource_drive_id is None or len(resource_drive_id) != 2 or resource_drive_id[0] is None:
        return False, "获取资源盘ID失败"

    data = requests.post("https://api.alipan.com/adrive/v3/file/search", headers={
        'Authorization': f'Bearer {access_token}'},
                         json={
                             "limit": 100,
                             "query": "category = \"doc\"",
                             "drive_file_list": [backup_drive_id[0], resource_drive_id[0]],
                             "order_by": random.choice(["name ASC", "created_at DESC", "updated_at DESC"])
                         }).json()

    if data is None:
        return False, "获取文档数据失败"

    items = data['items']
    if len(items) <= 0:
        return False, "获取文档数据失败"

    file_array = list()
    for i in range(0, len(items)):
        file_array.append({"drive_id": items[i]['drive_id'], "file_id": items[i]['file_id']})

    # 获取随机文件
    file_info = random.choice(file_array)
    data = requests.post(url='https://api.aliyundrive.com/adrive/v1/share/create', headers={
        'Authorization': f'Bearer {access_token}'},
                         json={"drive_file_list": [{"drive_id": file_info['drive_id'], "file_id": file_info['file_id']}]}).json()

    if 'share_id' in data:
        return True, '创建快传分享成功'
    elif 'display_message' in data and 'code' in data and data['code'] == 'CreateShareCountExceed':
        return True, data['display_message']
    else:
        return False, '创建快传失败，发生未知错误'


def play_video_by_mobile2(aligo=None, access_token=None):
    if aligo is None:
        return False, 'aligo 为空'

    if access_token is None:
        return False, 'access_token为空'
    # 首先获取备份盘的drive_id
    backup_drive_id = get_user_drive_id(aligo=aligo, category='backup')
    if backup_drive_id is None or len(backup_drive_id) != 2 or backup_drive_id[0] is None:
        return False, f'获取备份盘ID失败'

    # 首先获取资源盘的drive_id
    resource_drive_id = get_user_drive_id(aligo=aligo, category='resource')
    if resource_drive_id is None or len(resource_drive_id) != 2 or resource_drive_id[0] is None:
        return False, f'获取资源盘ID失败'

    # 获取备份盘和资源盘中所有包含视频的文件夹
    video_folder_list = requests.post(url='https://api.alipan.com/adrive/v2/video/list',
                                      headers={
                                          'Authorization': f'Bearer {access_token}'
                                      },
                                      json={
                                          "use_compilation": 'true',
                                          "duration": 0,
                                          "order_by": random.choice(["name asc", "created_at desc", "updated_at desc", "video_nums desc"]),
                                          "hidden_type": "NO_HIDDEN",
                                          # 备份盘和资源库
                                          "drive_id_list": [backup_drive_id[0], resource_drive_id[0]],
                                          "limit": 50})
    video_folder_list_json = None
    if video_folder_list.status_code == 200:
        video_folder_list_json = json.loads(video_folder_list.text)
    else:
        return False, '网络错误，请重试'

    if video_folder_list_json is None:
        return False, '没有获取到所有的视频文件夹数组，请确认资源库和备份库中是否存在视频文件'

    items = video_folder_list_json['items']
    # 视频文件ID数组，便后后续随机选择视频播放
    video_file_list = list()
    # 遍历视频文件夹，获取视频文件夹中的所有视频文件并放入数组，最多加入50个视频
    for i in range(len(items)):
        if 'video_hidden' in items[i] and items[i]['video_hidden'] is True:
            continue

        # 如果是视频文件，直接保存相关信息
        if 'category' in items[i] and items[i]['category'] == 'video' \
                and 'type' in items[i] and items[i]['type'] == 'file' \
                and 'status' in items[i] and items[i]['status'] == 'available' \
                and 'trashed' in items[i] and items[i]['trashed'] is False:
            duration = items[i]['duration']
            file_extension = items[i]['file_extension']
            file_name = items[i]['name']
            file_id = items[i]['file_id']
            drive_id = items[i]['drive_id']
            video_file_list.append({"duration": duration, "file_extension": file_extension, "file_name": file_name, "file_id": file_id, "drive_id": drive_id})
            # 选择最多50条视频
            if len(video_file_list) >= 50:
                break
            continue

        time.sleep(2)
        # 如果是文件夹，则获取文件夹中的视频
        video_list = requests.post(url='https://api.alipan.com/adrive/v2/video/compilation/list',
                                   headers={
                                       'Authorization': f'Bearer {access_token}'
                                   },
                                   json={
                                       "duration": 0,
                                       "order_by": random.choice(["name asc", "created_at desc", "updated_at desc"]),
                                       "hidden_type": "NO_HIDDEN",
                                       "name": items[i]['name'],
                                       "compilation_id": items[i]['compilation_id'],
                                       "limit": 50}).json()

        video_items = video_list['items']
        for j in range(len(video_items)):
            if 'type' not in video_items[j] or 'category' not in video_items[j] or 'hidden' not in video_items[j] or 'status' not in video_items[j] or 'trashed' not in video_items[j]:
                continue
            if video_items[j]['type'] == 'file' and video_items[j]['category'] == 'video' and video_items[j]['hidden'] is False and video_items[j]['status'] == "available":
                duration = video_items[j]['duration']
                file_extension = video_items[j]['file_extension']
                file_name = video_items[j]['name']
                file_id = video_items[j]['file_id']
                drive_id = video_items[j]['drive_id']
                video_file_list.append({"duration": duration, "file_extension": file_extension, "file_name": file_name, "file_id": file_id, "drive_id": drive_id})

        # 选择最多50条视频
        if len(video_file_list) >= 50:
            break

    if len(video_file_list) <= 0:
        return False, f'没有视频文件，请先上传多个大于30秒的视频至*{folder_name}*文件夹'

    # 随机选一个视频
    video_file = random.choice(video_file_list)
    duration = float(video_file['duration'])
    # 设置播放多长时间，在手机上每次暂停会调用该请求记录当前播放位置，所以一次性播放30秒，当大于35秒时，选择35秒视频，否则选择全部时长
    if duration > 35:
        play_cursor = 35 + round(random.random(), 6)
    else:
        play_cursor = duration + round(random.random(), 6)
    data = requests.post(
        'https://api.alipan.com/adrive/v2/video/update',
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        json={
            "play_cursor": play_cursor,
            "file_extension": video_file['file_extension'],
            "duration": duration,
            "name": video_file['file_name'],
            "file_id": video_file['file_id'],
            "drive_id": video_file['drive_id']
        },
    )
    if data.status_code == 400:
        return False, data.text
    # 是不是全部播放
    if data.status_code == 200:
        time.sleep(play_cursor)
        return True, '使用手机播放视频30s完毕'
    else:
        return False, '使用手机播放视频30s失败'


# 通过手机播放视频
def play_video_by_mobile(aligo=None, access_token=None):
    if aligo is None:
        return False, 'aligo 为空'

    if access_token is None:
        return False, 'access_token为空'
        # 首先获取备份盘的drive_id
    backup_drive_id = get_user_drive_id(aligo=aligo, category='backup')
    if backup_drive_id is None or len(backup_drive_id) != 2 or backup_drive_id[0] is None:
        return False, f'获取备份盘ID失败'

    # 获取文件夹下的视频
    folder_id = get_folder_id(aligo=aligo, _folder_name=folder_name, drive_id=backup_drive_id[0])
    if folder_id is None:
        return False, f'没有获取到*{folder_name}*文件夹'
    #  获取该文件夹下所有文件
    file_list = aligo.get_file_list(parent_file_id=folder_id, drive_id=backup_drive_id[0])
    if len(file_list) <= 0:
        return False, f'没有文件，请先上传多个大于30秒的视频至*{folder_name}*文件夹'

    file_id = None
    # 视频文件ID数组，便后后续随机选择视频播放
    file_id_list = list()
    for i in range(len(file_list)):
        if file_list[i].type is None or file_list[i].name is None:
            continue
        if file_list[i].type == 'file' and str(file_list[i].name).split('.')[1] in video_file_type:
            file_id = file_list[i].file_id
            file_id_list.append(file_id)

    if len(file_id_list) <= 0:
        return False, f'没有视频文件，请先上传多个大于30秒的视频至*{folder_name}*文件夹'

    # 随机选择视频
    file_id = random.choice(file_id_list)

    # 获取视频信息
    video_preview_play_info = aligo.get_video_preview_play_info(file_id=file_id, drive_id=backup_drive_id[0])
    # 获取播放总时长
    duration = video_preview_play_info.video_preview_play_info.meta.duration
    # 获取文件信息
    file_info = aligo.get_file(file_id=file_id, drive_id=backup_drive_id[0])
    # # 文件后缀
    file_extension = file_info.file_extension
    file_name = file_info.name

    # # 根据总时长划分每段请求的视频长度，以5为间隔
    # duration_list = numpy.arange(0, duration, 5, 'd')
    # count = 0
    # for i in range(len(list(duration_list))):
    #     if list(duration_list)[i] == 0:
    #         play_cursor = list(duration_list)[i] + round(random.random(), 6)
    #     else:
    #         play_cursor = list(duration_list)[i] + round(random.random(), 6)
    #     data = requests.post(
    #         'https://api.alipan.com/adrive/v2/video/update',
    #         headers={
    #             'Authorization': f'Bearer {access_token}'
    #         },
    #         json={
    #             "play_cursor": play_cursor,
    #             "file_extension": file_extension,
    #             "duration": duration,
    #             "name": file_name,
    #             "file_id": file_id,
    #             "drive_id": backup_drive_id[0]
    #         },
    #     )
    #     if data.status_code == 400:
    #         return False, data.text
    #     # 统计每个5秒间隔是不是全部播放
    #     if data.status_code == 200:
    #         count += 1
    #     # 以5为间隔休眠
    #     time.sleep(5)
    #
    # if count >= len(duration_list):
    #     return True, '使用手机播放视频30s完毕'
    # else:
    #     return False, '使用手机播放视频30s失败'

    # 设置播放多长时间，在手机上每次暂停会调用该请求记录当前播放位置，所以一次性播放30秒，当大于35秒时，选择35秒视频，否则选择全部时长
    if duration > 35:
        play_cursor = 35 + round(random.random(), 6)
    else:
        play_cursor = duration + round(random.random(), 6)
    data = requests.post(
        'https://api.alipan.com/adrive/v2/video/update',
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        json={
            "play_cursor": play_cursor,
            "file_extension": file_extension,
            "duration": duration,
            "name": file_name,
            "file_id": file_id,
            "drive_id": backup_drive_id[0]
        },
    )
    if data.status_code == 400:
        return False, data.text
    # 是不是全部播放
    if data.status_code == 200:
        time.sleep(play_cursor)
        return True, '使用手机播放视频30s完毕'
    else:
        return False, '使用手机播放视频30s失败'


# 暂时不使用，使用Windows播放视频和使用手机一样，Windows会获取m3u8，但是实际上还是要使用手机的api更新播放进度，单纯请求m3u8没办法完成播放视频任务
def play_video_by_windows(aligo=None, access_token=None):
    if aligo is None:
        return False, 'aligo 为空'

    if access_token is None:
        return 'access_token为空', False
    # 首先获取备份盘的drive_id
    backup_drive_id = get_user_drive_id(aligo=aligo, category='backup')
    if backup_drive_id is None or len(backup_drive_id) != 2 or backup_drive_id[0] is None:
        return False, f'获取备份盘ID失败'
    # 获取文件夹下的视频
    folder_id = get_folder_id(aligo=aligo, _folder_name=folder_name, drive_id=backup_drive_id[0])
    if folder_id is None:
        return False, f'没有获取到*{folder_name}*文件夹'
    #  获取该文件夹下所有文件
    file_list = aligo.get_file_list(parent_file_id=folder_id, drive_id=backup_drive_id[0])
    if len(file_list) <= 0:
        return False, f'没有视频文件，请先上传多个大于30秒的视频至*{folder_name}*文件夹'

    file_id = None
    # 视频文件ID数组，便后后续随机选择视频播放
    file_id_list = list()
    for i in range(len(file_list)):
        if file_list[i].type is None or file_list[i].name is None:
            continue
        if file_list[i].type == 'file' and str(file_list[i].name).split('.')[1] in video_file_type:
            file_id = file_list[i].file_id
            file_id_list.append(file_id)

    if len(file_id_list) <= 0:
        return False, f'没有视频文件，请先上传多个大于30秒的视频至*{folder_name}*文件夹'

    # 随机选择视频
    file_id = random.choice(file_id_list)

    # 获取文件信息
    file_info = aligo.get_file(file_id=file_id, drive_id=backup_drive_id[0])
    # # 文件后缀
    file_extension = file_info.file_extension
    file_name = file_info.name

    # 获取m3u8地址，然后分别请求每个m3u8,使用可以使用的清晰度
    video_preview_play_info_response = aligo.get_video_preview_play_info(file_id=file_id, drive_id=backup_drive_id[0])
    # 获取播放时长
    duration = video_preview_play_info_response.video_preview_play_info.meta.duration
    # 获取所有的清晰度
    live_transcoding_task_list = video_preview_play_info_response.video_preview_play_info.live_transcoding_task_list
    if len(live_transcoding_task_list) <= 0:
        return False, '没有可用的清晰度'
    # 遍历得到可以用的清晰度
    m3u8_url = None
    for i in range(len(live_transcoding_task_list)):
        if live_transcoding_task_list[i].status == "finished":
            m3u8_url = live_transcoding_task_list[i].url
            break

    if m3u8_url is None:
        return False, '没有解析出m3u8地址'
    # 解析host
    url_parse = urlparse(url=m3u8_url)
    if url_parse is None or url_parse.hostname is None or len(url_parse.hostname) <= 0:
        return False, '没有解析出host地址'
    header = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Host': url_parse.hostname,
        'Origin': 'https://www.aliyundrive.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.aliyundrive.com/',
        'Sec-Ch-Ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': 'Windows',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    # 解析m3u8
    play_list = m3u8.load(m3u8_url, headers=header, verify_ssl=False)
    count = 0
    # 请求m3u8，请求的时长不超过35秒
    for index, segment in enumerate(play_list.segments):
        # ur = segment.uri
        duration = segment.duration
        absolute_uri = segment.absolute_uri
        requests.get(absolute_uri, headers=header, verify=False)

    time.sleep(3)
    if duration > 35:
        play_cursor = 35 + round(random.random(), 6)
    else:
        play_cursor = duration + round(random.random(), 6)
    # 请求最多35秒的视频
    data = requests.post(
        'https://api.alipan.com/adrive/v2/video/update',
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        json={
            "play_cursor": play_cursor,
            "file_extension": file_extension,
            "duration": duration,
            "name": file_name,
            "file_id": file_id,
            "drive_id": backup_drive_id[0]
        },
    )
    if data.status_code == 400:
        return False, data.text
    # 统计是不是全部播放
    if data.status_code == 200:
        time.sleep(play_cursor)
        return True, '使用Windows播放视频30s完毕'
    else:
        return False, '使用Windows播放视频30s失败'


def follow_user(user_id=None, session=None, access_token=None, time_sleep=0):
    if access_token is None:
        return 'access_token为空', False
    if session is None:
        return 'session为空', False
    if user_id is None:
        user_id = alipanpanjiang_id
    try:
        resp = session.post('https://api.aliyundrive.com/adrive/v1/member/follow_user',
                            headers={
                                'Authorization': f'Bearer {access_token}'
                            },
                            body={
                                'user_id': user_id
                            })
        if resp.status_code == 200:
            return '订阅成功', True
    except Exception as e:
        return '订阅阿里盘酱酱出现异常，请手动尝试', False


# 捞好运瓶任务
def get_lucky_bittle(access_token=None, session=None, time_sleep=0):
    if access_token is None:
        return 'access_token为空', False
    if session is None:
        return 'session为空', False

    # 任务需要捞取3次
    lucky_bittle_need_count = 3

    #     获取当前次数
    # {
    # 创建好运瓶限制
    # 	"createBottleLimit": 100,
    # 已使用好运瓶限制
    # 	"createBottleUsed": 0,
    # 捞取总数
    # 	"fishBottleLimit": 3,
    # 已经捞取数
    # 	"fishBottleUsed": 1
    # }
    try:
        resp = session.post('https://api.alipan.com/adrive/v1/bottle/getUserLimit',
                            headers={
                                'Authorization': f'Bearer {access_token}'
                            },
                            json={}).json()
        if 'fishBottleUsed' in resp and 'fishBottleLimit' in resp:
            fishBottleLimit = int(resp['fishBottleLimit'])
            fishBottleUsed = int(resp['fishBottleUsed'])

            # 根据当前任务最多捞取3次
            if fishBottleLimit > lucky_bittle_need_count:
                fishBottleLimit = lucky_bittle_need_count
            # 如果用户已经捞取的数目大于等于每日要求的数目
            if fishBottleUsed >= lucky_bittle_need_count:
                return f'已经成功捞取{fishBottleUsed}次好运瓶', True

            # 捞取剩余次数的好运瓶
            for i in range(lucky_bittle_need_count - fishBottleUsed):
                resp = session.post('https://api.alipan.com/adrive/v1/bottle/fish',
                                    headers={
                                        'Authorization': f'Bearer {access_token}'
                                    },
                                    json={})
                if resp.status_code == 200:
                    fishBottleUsed += 1
                time.sleep(time_sleep)

            if fishBottleUsed >= lucky_bittle_need_count:
                return f'已经成功捞取{lucky_bittle_need_count}次好运瓶', True
            else:
                return f'已经捞取{fishBottleUsed}次好运瓶,还需要手动捞取{lucky_bittle_need_count - fishBottleUsed}次可领取奖励', False
    except Exception as e:
        return f'捞取好运瓶出现异常，请手动尝试', False


# 创建文件夹
def my_create_folder(aligo=None, _folder_name=None, time_sleep=0, drive_id=None, drive_name=None, category=None):
    if aligo is None:
        return None
    if _folder_name is None:
        _folder_name = folder_name

    if drive_id is None or len(drive_id) <= 0:
        # 首先获取备份盘的drive_id
        backup_drive_id = get_user_drive_id(aligo=aligo, drive_name=drive_name, category=category)
        if backup_drive_id is None or len(backup_drive_id) != 2 or backup_drive_id[0] is None:
            return None
        else:
            drive_id = backup_drive_id[0]
    folder_id = None
    response = aligo.create_folder(name=_folder_name, check_name_mode='refuse', drive_id=drive_id)
    if response is not None:
        folder_id = response.file_id
    else:
        return None

    return folder_id


# 获取文件夹id根据名称
def get_folder_id(aligo=None, _folder_name=None, time_sleep=0, drive_id=None):
    if aligo is None:
        return None

    if drive_id is None:
        return None

    if _folder_name is None:
        _folder_name = folder_name

    folder_id = None
    # 获取备份盘下所有的文件夹，寻找默认名称为阿里云盘签到任务文件夹
    file_list = aligo.get_file_list(drive_id=drive_id)
    for i in range(len(file_list)):
        if file_list[i].type is None or file_list[i].name is None:
            continue
        if file_list[i].type == 'folder' and file_list[i].name == _folder_name:
            folder_id = file_list[i].file_id
            break

    return folder_id


# 删除上次创建的相册，
def delete_lastTime_album(aligo=None):
    if aligo is None:
        return False, 'aligo 为空'

    yesterday = datetime.date.today() + datetime.timedelta(days=-1)
    album_list = aligo.list_albums()
    if len(album_list) <= 0:
        return True, ''

    for i in range(len(album_list)):
        if album_list[i].type is None or album_list[i].name is None:
            continue
        if 'manual' == album_list[i].type and album_list[i].name == create_album_name:
            aligo.delete_album(album_list[i].album_id)
            break

    return True, ''


# 创建手工相册，也可以创建上传图片任务相册，根据type确定,album_type=0:创建上传图片任务相册，album_type=1：创建手工相册
def create_album(aligo=None, album_name=None, path=None, time_sleep=0, album_type=None):
    if aligo is None:
        return False, 'aligo 为空'

    if album_type is None:
        return False, 'album_type 为空'

    description = None
    if album_name is None:
        if album_type == 0:
            album_name = upload_photo_album_name
            description = upload_photo_album_name
        elif album_type == 1:
            album_name = create_album_name
            description = create_album_name
        else:
            return False, 'album_type 只能为0或者1'
    response = aligo.create_album(name=album_name, description=description)

    if response is not None:
        return response.album_id, True
    else:
        return None, False


# 此方法会删除 阿里云盘签到任务文件夹  下的所有文件
def delete_file(aligo=None, _folder_name=None, time_sleep=0):
    if aligo is None:
        return 'aligo 为空', False
    if _folder_name is None:
        _folder_name = folder_name

    try:
        #     获取 备份盘下 '阿里云盘签到任务文件夹'的ID
        # 首先获取备份盘的drive_id
        backup_drive_id = get_user_drive_id(aligo=aligo, category='backup')
        if backup_drive_id is None or len(backup_drive_id) != 2 or backup_drive_id[0] is None:
            return f'获取 备份盘ID失败,无法删除文件,请手动删除', False

        folder_id = get_folder_id(aligo, _folder_name=_folder_name, drive_id=backup_drive_id[0])
        if folder_id is None:
            return f'获取 *{_folder_name}* 文件夹失败,无法删除文件,请手动删除', True
        else:
            #  获取该文件夹下所有文件
            file_list = aligo.get_file_list(parent_file_id=folder_id, drive_id=backup_drive_id[0])
            if len(file_list) <= 0:
                return '', True

            for i in range(len(file_list)):
                if file_list[i].type is None or file_list[i].name is None or file_list[i].mime_extension is None:
                    continue
                #     不删除视频文件
                elif file_list[i].category == 'video' and (file_list[i].type == 'file' and file_list[i].mime_extension in video_file_type):
                    continue
                else:
                    aligo.move_file_to_trash(file_id=file_list[i].file_id, drive_id=backup_drive_id[0])

            return '文件删除成功', True
    except Exception as e:
        raise Exception('删除文件:' + str(e))


# 删除该相册下的所有文件
def delete_photo_from_album(aligo=None, album_id=None, time_sleep=0):
    if aligo is None:
        return 'aligo 为空', False

    try:
        # 获取相册id
        album_list = aligo.list_albums()
        if len(album_list) <= 0:
            return '', True

        for i in range(len(album_list)):
            if album_list[i].type is None or album_list[i].name is None:
                continue

            if 'manual' == album_list[i].type and album_list[i].name == upload_photo_album_name:
                album_id = album_list[i].album_id
                break
        if album_id is None:
            return f'找不到名为 {upload_photo_album_name} 的相册', True
        # 获取相册图片
        photo_list = aligo.list_album_files(album_id)
        if len(photo_list) <= 0:
            return '相册中图片为空', True

        # 获取相册drive的id
        album_drive_id = get_user_drive_id(aligo=aligo, drive_name='alibum')
        if album_drive_id is None or len(album_drive_id) != 2:
            return '没有获取到相册drive的id', False, None

        for i in range(len(photo_list)):
            # batch_photo_id.append(response[i].file_id)
            aligo.move_file_to_trash(file_id=photo_list[i].file_id, drive_id=album_drive_id[0])

        return '删除照片成功', True
    except Exception as e:
        return '删除照片异常:' + str(e), False


# 上传10张照片,首先判断相册是否存在，相册不存在先创建相册，再上传图片并删除本地图片
def upload_photo(aligo=None, path=None, time_sleep=0, photo_num=10):
    if aligo is None:
        return 'aligo 为空', False, None

    if path is None:
        return 'path 为空', False, None

    try:
        # 本地文件夹不存在，则创建
        if os.path.exists(path) is False:
            os.makedirs(path)
        #     获取相册列表
        list_albums = aligo.list_albums()
        albums_id = None
        for i in range(len(list_albums)):
            if list_albums[i].type is None or list_albums[i].name is None:
                continue
            if 'manual' == list_albums[i].type and list_albums[i].name == upload_photo_album_name:
                albums_id = list_albums[i].album_id
                break

        # 相册不存在，创建相册
        if albums_id is None:
            albums_id, is_success = create_album(aligo, album_type=0)
            if albums_id is None or is_success is False:
                return '创建相册失败,请手动完成该任务', False, None

        # # 获取所有的文件夹，寻找默认名称为阿里云盘签到任务文件夹
        # folder_id = get_folder_id(aligo, _folder_name=folder_name)
        # # auto_rename 自动重命名，存在并发问题
        # # refuse 同名不创建，直接返回已经存在的
        # # ignore 同名文件可创建
        # # 不存在则创建文件夹
        # if folder_id is None:
        #     folder_id = my_create_folder(aligo, _folder_name=folder_name)
        #     if folder_id is None:
        #         return '上传图片时创建文件夹失败', False, None

        #     生成10个图片，并上传，上传完毕后删除本地图片
        #     从本地添加需要先上传到相册，然后再移动到指定的相薄中
        success_count = 0
        # 获取相册drive的id
        album_drive_id = get_user_drive_id(aligo=aligo, drive_name='alibum')
        if album_drive_id is None or len(album_drive_id) != 2 or album_drive_id[0] is None:
            return '没有获取到相册drive的id', False, None

        # 生成10个图片并上传，上传成功后删除本地图片
        for i in range(photo_num):
            im = Image.new('RGB', (200, 200), color="red")
            file_name = f'{str(int(round(time.time() * 1000))) + "_" + str(i + 1)}.jpg'
            im.save(f'{path + "/" + file_name}')
            # 先上传到默认的相册薄中，此时并未指定相册
            f = aligo.upload_file(f'{path + "/" + file_name}', parent_file_id='root', drive_id=album_drive_id[0])
            # 移动相片到指定的相薄
            result = aligo.add_files_to_album(files=[f], album_id=albums_id)
            # 上传成功后删除本地文件
            if result is not None:
                os.remove(path + "/" + file_name)
                success_count += 1

        if success_count == photo_num:
            return '', True, albums_id
        else:
            return '上传照片失败,请手动完成该任务', False, None

    except Exception as e:
        return '上传照片失败,请手动完成该任务', False, None


# 上传10个文件，首先创建一个文件夹，上传到指定的文件夹,首先判断文件夹是否存在，不存在则创建，如果存在则上传文件
def upload_file(aligo=None, path=None, time_sleep=0, file_num=10):
    if aligo is None:
        return 'aligo 为空', False

    if path is None:
        return 'path 为空', False
    try:
        # 本地文件夹不存在，则创建
        if os.path.exists(path) is False:
            os.makedirs(path)
        # 获取所有的文件夹，寻找默认名称为阿里云盘签到任务文件夹
        # 首先获取备份盘的drive_id
        backup_drive_id = get_user_drive_id(aligo=aligo, category='backup')
        if backup_drive_id is None or len(backup_drive_id) != 2 or backup_drive_id[0] is None:
            return f'获取 备份盘ID失败', False

        folder_id = get_folder_id(aligo, _folder_name=folder_name, drive_id=backup_drive_id[0])
        # auto_rename 自动重命名，存在并发问题
        # refuse 同名不创建，直接返回已经存在的
        # ignore 同名文件可创建
        # 不存在创建文件夹
        if folder_id is None:
            folder_id = my_create_folder(aligo, _folder_name=folder_name, drive_id=backup_drive_id[0])
            if folder_id is None:
                return '上传文件时创建文件夹失败', False

        # 生成10个文件，并上传到该文件夹，然后删除文件
        success_count = 0

        for i in range(file_num):
            file_name = f'{str(int(round(time.time() * 1000))) + "_" + str(i + 1)}.txt'
            with open(path + '/' + file_name, encoding='utf-8', mode='w') as f:
                f.write(f'{str(int(round(time.time() * 1000))) + "_" + str(i + 1)}.txt')
            # 上传文件
            result = aligo.upload_files(file_paths=[path + '/' + file_name], parent_file_id=folder_id, drive_id=backup_drive_id[0])
            # 上传成功后删除文件
            if result is not None:
                os.remove(path + '/' + file_name)
                success_count += 1

        if success_count == file_num:
            return '', True
        else:
            return '上传文件失败,请手动完成该任务', False
    except Exception as e:
        return f'上传文件失败,请手动完成该任务,错误信息：{e}', False
