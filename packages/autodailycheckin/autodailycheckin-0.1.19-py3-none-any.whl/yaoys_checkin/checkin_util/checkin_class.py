# -*- coding: utf-8 -*-
# @FileName  :checkin_class.py
# @Time      :2023/4/7 22:46
# @Author    :yaoys
# @Desc      :

from yaoys_checkin.ablesci_checkin.ableSci_checkin import ableSci
from yaoys_checkin.aliyunpan_checkin.aliyunpan_checkin import aliyunpan
from yaoys_checkin.bilibili_checkin.bilibili_alive_auto_checkin import bilibili_alive
from yaoys_checkin.bilibili_checkin.bilibili_auto_checkin import bilibili_coin
from yaoys_checkin.cloud_189_checkin.cloud189_checkin import cloud189
from yaoys_checkin.glados_checkin.glados import glados
from yaoys_checkin.gufenxueshu_checkin.gufen_checkin import gufenxueshu
from yaoys_checkin.hifini_checkin.hifini_autoCheckin import hifini
from yaoys_checkin.jiaoyimao.jiaoyimao_checkin import jiaoyimao
from yaoys_checkin.legado.legado_checkin import Leado
from yaoys_checkin.piaoyunge.piaoyunge_checkin import piaoyunge
from yaoys_checkin.push_message.push_message import pushPlus, server
from yaoys_checkin.tieba_checkin.tieba_checkin import tieba
from yaoys_checkin.wps_checkin.wps_cloud_checkin import wps_cloud
from yaoys_checkin.wps_checkin.wps_vip_checkin import wps_vip
from yaoys_checkin.wuaipojie_checkin.wuaipojie import wuaipojie_checkin

checkin_class = {
    "able_sci": {
        "task_name": "科研通平台",
        "cookie_name": "able_sci",
        "task_class_name": ableSci,
        # 如果一个平台涉及多个账号签到时每个账号签到完毕后休眠时间
        # "more_time_sleep": 0,
        # 多个平台之间签到间隔
        # "time_sleep": 0,
        "desc": "科研通平台相关配置",
        # 该平台签到是否有效
        "is_used": True
    },
    "bilibili_live": {
        "task_name": "B站直播",
        "cookie_name": "bilibili_live",
        "task_class_name": bilibili_alive,
        # "more_time_sleep": 10,
        # "time_sleep": 0,
        "desc": "B站直播签到平台相关配置",
        # 该平台签到是否有效
        "is_used": True
    },
    "bilibili_icon": {
        "task_name": "B站获取硬币",
        "cookie_name": "bilibili_icon",
        "task_class_name": bilibili_coin,
        # "more_time_sleep": 10,
        # "time_sleep": 0,
        "desc": "B站获取硬币相关配置",
        # 该平台签到是否有效
        "is_used": True
    },
    "cloud189": {
        "task_name": "天翼云网盘",
        "cookie_name": "cloud189",
        "task_class_name": cloud189,
        # "more_time_sleep": 10,
        # "time_sleep": 0,
        "desc": "天翼云盘相关配置",
        # 该平台签到是否有效
        "is_used": True
    },
    "glados": {
        "task_name": "glados平台",
        "cookie_name": "glados",
        "task_class_name": glados,
        # "more_time_sleep": 10,
        # "time_sleep": 0,
        "desc": "glados平台相关配置",
        # 该平台签到是否有效
        "is_used": True
    },
    "gu_fen_xue_shu": {
        "task_name": "谷粉学术",
        "cookie_name": "gu_fen_xue_shu",
        "task_class_name": gufenxueshu,
        # "more_time_sleep": 10,
        # "time_sleep": 0,
        "desc": "谷粉学术平台相关配置",
        # 该平台签到是否有效
        "is_used": True
    },
    "aliyunpan": {
        "task_name": "阿里云盘",
        "cookie_name": "aliyunpan",
        "task_class_name": aliyunpan,
        # "more_time_sleep": 10,
        # "time_sleep": 0,
        "desc": "阿里云盘相关配置",
        # 该平台签到是否有效
        "is_used": True
    },
    "wps_vip": {
        "task_name": "wps_vip",
        "cookie_name": "wps_vip",
        "task_class_name": wps_vip,
        # "more_time_sleep": 20,
        # "time_sleep": 0,
        "desc": "Wps Vip相关配置",
        # 该平台签到是否有效
        "is_used": False
    },
    "wps_cloud": {
        "task_name": "wps_cloud",
        "cookie_name": "wps_cloud",
        "task_class_name": wps_cloud,
        # "more_time_sleep": 20,
        # "time_sleep": 0,
        "desc": "Wps云空间相关配置",
        # 该平台签到是否有效
        "is_used": True
    },
    "tieba": {
        "task_name": "百度贴吧",
        "cookie_name": "tieba",
        "task_class_name": tieba,
        # "more_time_sleep": 10,
        # "time_sleep": 0,
        "desc": "百度贴吧相关配置",
        # 该平台签到是否有效
        "is_used": True
    },
    "wuaipojie": {
        "task_name": "吾爱破解",
        "cookie_name": "wuaipojie",
        "task_class_name": wuaipojie_checkin,
        # "more_time_sleep": 15,
        # "time_sleep": 0,
        "desc": "吾爱破解相关配置",
        # 该平台签到是否有效
        "is_used": False
    },
    "jiaoyimao": {
        "task_name": "交易猫",
        "cookie_name": "jiaoyimao",
        "task_class_name": jiaoyimao,
        # "more_time_sleep": 10,
        # "time_sleep": 0,
        "desc": "交易猫相关配置",
        # 该平台签到是否有效
        "is_used": True
    },
    "piaoyunge": {
        "task_name": "飘云阁",
        "cookie_name": "piaoyunge",
        "task_class_name": piaoyunge,
        # "more_time_sleep": 10,
        # "time_sleep": 0,
        "desc": "飘云阁相关配置",
        # 该平台签到是否有效
        "is_used": True
    },
    "hifini": {
        "task_name": "hifini音乐网站",
        "cookie_name": "hifini",
        "task_class_name": hifini,
        # "more_time_sleep": 10,
        # "time_sleep": 0,
        "desc": "hifini音乐网站相关配置",
        # 该平台签到是否有效
        "is_used": True
    },
    "legado": {
        "task_name": "legado阅读网站",
        "cookie_name": "legado",
        "task_class_name": Leado,
        # "more_time_sleep": 10,
        # "time_sleep": 0,
        "desc": "legado阅读网站",
        # 该平台签到是否有效
        "is_used": False
    },

}

message_class = {
    'pushPlus': ['pushPlus', pushPlus],
    'server': ['server', server]
}
