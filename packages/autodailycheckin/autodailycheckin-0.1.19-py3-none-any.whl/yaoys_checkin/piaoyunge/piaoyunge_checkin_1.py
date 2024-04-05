# -*- coding: utf-8 -*-
# @FileName  :piaoyunge_checkin.py
# @Time      :2023/7/10 19:38
# @Author    :yaoys
# @Desc      :
import warnings

import requests
from requests.cookies import cookiejar_from_dict

warnings.filterwarnings('ignore')
header = {
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
cookie = ''
cookie_dict = {i.split("=")[0]: i.split("=")[1] for i in cookie.split("; ")}
# cookie_dict = {i.split("=")[0]: i.split("=")[1] for i in cookie.split("; ")}
data = {
    'formhash': '8269f797',
    'qdxq': 'kx',
    'qdmode': '2',
    'todaysay': '',
    'fastreply': '0'
}
session = requests.session()
resp = requests.post(url='https://www.chinapyg.com/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&sign_as=1&inajax=1',
                     headers=header,
                     verify=False,
                     cookies=cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True),
                     data=data,
                     timeout=5)

print(resp.text)
