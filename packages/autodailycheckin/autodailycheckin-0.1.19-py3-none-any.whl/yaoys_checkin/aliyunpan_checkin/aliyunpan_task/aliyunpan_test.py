# -*- coding: utf-8 -*-
# @FileName  :aliyunpan_test.py
# @Time      :2023/8/7 22:04
# @Author    :yaoys
# @Desc      :
import re
import time

import m3u8
import numpy
import requests
from aligo import Aligo, set_config_folder

# 手机版
# 使用159账号
set_config_folder(path='D:\project\Auto_checkin_desktop_source_code\\config')
ali = Aligo(refresh_token=None, level=50, name='阿里云盘账号_1', re_login=False)

list_drive = ali.list_my_drives()

for i in range(len(list_drive)):
    if list_drive[i].drive_name is None:
        continue
    if list_drive[i].drive_type == 'normal' and list_drive[i].drive_name == 'Default' and list_drive[i].status == 'enabled' and list_drive[i].category == 'backup':
        print(list_drive[i].drive_id)
# print(list_drive)
# data = requests.post(url='https://api.alipan.com/adrive/v1/albumHome/summary', headers={
#     'Authorization': ''},
#                      json={"album_drive_id": "23919250", "drive_id": "613087872"}).json()
#
# print(data)

# 上传照片到相册
# 请求数据
# https://api.alipan.com/adrive/v2/file/createWithFolders
# json数据
# {
# 	"content_hash": "C3D33E2ACF057A369E917699E319C0E4FA291708",
# 	"proof_code": "+FX/AIX/AIU=",
# 	"user_meta": "{\"size\":750202,\"hash\":\"AF8FE6090BB16E785CE415F14E0BC43687A95A96\",\"identifier\":\"93FEDA06-F3D6-41B8-8969-A992B07DB33D\\/L0\\/001\",\"time\":1680710246256,\"duration\":0}",
# 	"create_scene": "file_upload",
# 	"parent_file_id": "root",
# 	"content_hash_name": "sha1",
# 	"type": "file",
# 	"size": 750202,
# 	"content_type": "image/jpeg",
# 	"device_name": "iPhone14,5",
# 	"drive_id": "17844501",
# 	"auto_rename": false,
# 	"check_name_mode": "auto_rename",
# 	"hidden": false,
# 	"proof_version": "v1",
# 	"name": "IMG_2534.JPG",
# 	"image_media_metadata": {
# 		"width": 909,
# 		"height": 1662
# 	}
# }

# 默认上传到相册，但是没有到指定的相册中
# response = ali.upload_file(file_path='D:\project\Auto_checkin_desktop_source_code\\aliyunpan_daily_task\\album\\1691495972952_1.jpg', parent_file_id='root', name='aaa.jpg', drive_id='17844501')
# print(response)

#
# file_list = ali.get_file_list(parent_file_id='64d57abbce267493a67d4f708cc2619542a1b188', drive_id=ali.default_drive_id)
# length = len(file_list)
# print(length)
# for i in range(len(file_list)):
#     if file_list[i].type is None or file_list[i].name is None:
#         continue
#     #     不删除视频文件
#     #     不删除视频文件
#     if file_list[i].category == 'video' and (file_list[i].type == 'file' and str(file_list[i].name).split('.')[1] in ['mp4', 'flv']):
#         continue
#     print(file_list[i].type == 'file')
# print(ali.get_drive())
# data = requests.post(url='https://api.aliyundrive.com/adrive/v1/share/create', headers={
#     'Authorization': f'Bearer {None}'},
#                      json={"drive_file_list": [{"drive_id": "158277", "file_id": "64d777a7899e02bf0ab042fd92442d4eeb36ead6"}]})
# #
# # 点击链接即可保存。「阿里云盘」APP ，无需下载极速在线查看，视频原画倍速播放。","share_title":"我给你发了 do...eo.mp4, 快来看看","share_subtitle":"点击卡片即可保存。「阿里云盘」APP ，无需下载极速在线查看，视频原画。","expired":false}
#
# # 403  {"code":"CreateShareCountExceed","message":"create share count limit exceed","requestId":"0a0070d716918921648113014ef89d","resultCode":"CreateShareCountExceed","display_message":"今日快传次数已达上限"}
# print(data.text)
# print(ali.get_file_list(parent_file_id='64d57abbce267493a67d4f708cc2619542a1b188'))
# resp = ali.create_folder(name='测试文件夹')
# print(resp)
# ali.create_album(name='阿里云盘任务', description='阿里云盘签到任务')
# '64d2302fe3a4c6b9f4414496ba5490d6aae462ec'  '158712'
# 获取相册中的图片
# response = ali.get_video_preview_play_info(file_id='64d777a7899e02bf0ab042fd92442d4eeb36ead6', drive_id='158277')
# print(response)
# # 获取播放总时长
# duration = response.video_preview_play_info.meta.duration
# print(duration)
# # 获取文件的信息
# file_info = ali.get_file(file_id='64d777a7899e02bf0ab042fd92442d4eeb36ead6', drive_id='158277')
# # 文件后缀
# file_extension = file_info.file_extension
# file_name = file_info.name
# print(file_extension)
#
# # 根据总时长划分每段请求的视频长度，以5为间隔
# duration_list = numpy.arange(0, duration, 5, 'd')
# print(list(duration_list))
# for i in range(len(list(duration_list))):
#     data = requests.post(
#         'https://api.alipan.com/adrive/v2/video/update',
#         headers={
#             'Authorization':
#                 "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9"
#                 ".eyJ1c2VySWQiOiI3Yzc5N2ZkZDYyYjA0MDIwYTY0N2MyNDUzNjYwZDAzZSIsImN1c3RvbUpzb24iOiJ7XCJjbGllbnRJZFwiOlwiMjVkelgzdmJZcWt0Vnh5WFwiLFwiZG9tYWluSWRcIjpcImJqMjlcIixcInNjb3BlXCI6W1wiRFJJVkUuQUxMXCIsXCJTSEFSRS5BTExcIixcIkZJTEUuQUxMXCIsXCJVU0VSLkFMTFwiLFwiVklFVy5BTExcIixcIlNUT1JBR0UuQUxMXCIsXCJTVE9SQUdFRklMRS5MSVNUXCIsXCJCQVRDSFwiLFwiT0FVVEguQUxMXCIsXCJJTUFHRS5BTExcIixcIklOVklURS5BTExcIixcIkFDQ09VTlQuQUxMXCIsXCJTWU5DTUFQUElORy5MSVNUXCIsXCJTWU5DTUFQUElORy5ERUxFVEVcIl0sXCJyb2xlXCI6XCJ1c2VyXCIsXCJyZWZcIjpcImh0dHBzOi8vd3d3LmFsaXl1bmRyaXZlLmNvbS9cIixcImRldmljZV9pZFwiOlwiYjA3MjIyZDhjNzk1NGYyNjg2ODgzZmMzNzBhYzQ5MmZcIn0iLCJleHAiOjE2OTE4NTAyMDksImlhdCI6MTY5MTg0Mjk0OX0.JxMOoaQviTDT4vbMzUpdIWKTfkaaxd8YFlPacu4dm8rIxzlmo5E3-OWUBvXSWZyz-tVH3gzR6opYN5pLsGIVwPEgIX-wQFbFqUjFXVj7sKZ23TIw-Y-5mUT2_jVCC8G9sBXpN4y4hSu_3mowAODQ4PjZEX8EQ-CXrrZK9r1QwHg"
#         },
#         json={
#             "play_cursor": list(duration_list)[i],
#             "file_extension": file_extension,
#             "duration": duration,
#             "name": file_name,
#             "file_id": "64d777a7899e02bf0ab042fd92442d4eeb36ead6",
#             "drive_id": "158277"
#         },
#     )
#     print(data.text)
#     time.sleep(3)
# 获取播放信息{
# 	"play_cursor": "0.348",
# 	"file_extension": "mp4",
# 	"duration": "0.348",
# 	"name": "downloadVideo.mp4",
# 	"file_id": "64d777a7899e02bf0ab042fd92442d4eeb36ead6",
# 	"drive_id": "158277"
# }
# 删除图片
# batch_photo_id = list()
# for i in range(len(response)):
#     # batch_photo_id.append(response[i].file_id)
#     ali.move_file_to_trash(file_id=response[i].file_id, drive_id=ali.default_drive_id)
# result = ali.upload_files(file_paths=['E:\log\kugan\log\debug\log-debug-2021-08-14.0.log', 'E:\log\kugan\log\debug\log-debug-2021-08-15.0.log'], parent_file_id='64d0fbae5615ca7abe5747ce8a1f8abaeb52413d')
# print(result)
# file_list = ali.get_file_list()
# assert isinstance(file_list, list)
# print(file_list)
#
# for i in range(len(file_list)):
#     print(file_list[i].name)

# 电脑版：
#
# # 首先获取m3u8地址，然后分别请求每个m3u8,使用最低清晰度避免无会员，即标清
# response = ali.get_video_preview_play_info(file_id='64d777a7899e02bf0ab042fd92442d4eeb36ead6', drive_id='158277')
# # 获取所有的清晰度
# live_transcoding_task_list = response.video_preview_play_info.live_transcoding_task_list
# # 遍历得到可以用的清晰度
# m3u8_url = ''
# for i in range(len(live_transcoding_task_list)):
#     if live_transcoding_task_list[i].status == "finished":
#         m3u8_url = live_transcoding_task_list[i].url
#         break
# from urllib.parse import urlparse
#
# print(m3u8_url)
# url_parse = urlparse(url=m3u8_url)
# print(url_parse.hostname)
# # 解析host
# s = re.findall(r'https://(.*?)/', m3u8_url)
# print(s)
# header = {
#     'Accept': '*/*',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
#     'Cache-Control': 'no-cache',
#     'Host': s[0],
#     'Origin': 'https://www.aliyundrive.com',
#     'Pragma': 'no-cache',
#     'Referer': 'https://www.aliyundrive.com/',
#     'Sec-Ch-Ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
#     'Sec-Ch-Ua-Mobile': '?0',
#     'Sec-Ch-Ua-Platform': 'Windows',
#     'Sec-Fetch-Dest': 'empty',
#     'Sec-Fetch-Mode': 'cors',
#     'Sec-Fetch-Site': 'cross-site',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
# }
# # m3u8_text = requests.get(m3u8_url, headers=header).text
# # print(m3u8_text)
# play_list = m3u8.load(m3u8_url, headers=header, verify_ssl=False)
# count = 0
# for index, segment in enumerate(play_list.segments):
#     # ur = segment.uri
#     duration = segment.duration
#     url = segment.uri
#     absolute_uri = segment.absolute_uri
#     data = requests.get(absolute_uri, headers=header, verify=False)
#     if data.status_code == 200:
#         count += duration
#     if count >= 30:
#         break
#
#     time.sleep(duration)
#
# print(count)
