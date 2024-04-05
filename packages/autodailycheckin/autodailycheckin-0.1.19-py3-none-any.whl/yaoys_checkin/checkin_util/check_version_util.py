# -*- coding: utf-8 -*-
# @FileName  :check_version_util.py
# @Time      :2023/7/11 11:49
# @Author    :yaoys
# @Desc      :
import json
from itertools import zip_longest

import requests

from yaoys_checkin.__version__ import autocheckin_version as current_version


def compareVersion(version1: str, version2: str) -> int:
    for v1, v2 in zip_longest(version1.split('.'), version2.split('.'), fillvalue=0):
        x, y = int(v1), int(v2)
        if x != y:
            return True if x > y else False
    return False


def query_release_notes():
    try:
        release_url = (
            "https://github.com/yaoysyao/Auto_checkin_release/blob/master/version.json"
        )
        content = requests.get(release_url, timeout=5)
        release_note = content.json()
        for v in json.loads(release_note['payload']['blob']['rawBlob'])['version'][0].values():
            if compareVersion(v, current_version):
                return f'当前最新版本为 {v}，请前往：https://github.com/yaoysyao/Auto_checkin_release/ 获取最新版本\n'
            else:
                return '当前已是最新版本，无需更新\n'
        # print(json.loads(release_note['payload']['blob']['rawBlob'])['version'][0].keys())

        # print(release_note["1.16.25"])
    except Exception as e:
        try:
            release_url = (
                "https://gitee.com/yaoys95/Auto_checkin_release/raw/master/version.json"
            )
            content = requests.get(release_url, timeout=5)
            release_note = content.json()
            # #方法1：获取value值
            for v in release_note['version'][0].values():
                if compareVersion(v, current_version):
                    return f'当前最新版本为 {v}，请前往：https://github.com/yaoysyao/Auto_checkin_release/ 获取最新版本\n'
                else:
                    return '当前已是最新版本，无需更新\n'
        except Exception as e:
            return '版本信息获取失败，请前往 https://github.com/yaoysyao/Auto_checkin_release/ 查看最新版本\n'

# # query_release_notes()
#
# print(compareVersion('0.1.2', '0.1.3'))
