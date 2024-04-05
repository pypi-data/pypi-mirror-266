# -*- coding: utf-8 -*-
# @FileName  :piaoyunge_checkin_获取fromhash.py
# @Time      :2023/7/10 20:07
# @Author    :yaoys
# @Desc      :
import re
import warnings
from bs4 import BeautifulSoup
import requests
from requests.cookies import cookiejar_from_dict

warnings.filterwarnings('ignore')
header = {
    'Host': 'www.chinapyg.com',
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': 'Windows',
    'Accept': '*/*',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.chinapyg.com/forum.php?mod=viewthread&tid=147569&page=1',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}
cookie = ''
cookie_dict = {i.split("=")[0]: i.split("=")[1] for i in cookie.split("; ")}
# yys5183: <input type="hidden" name="formhash" value="d96188ea">
resp = requests.post(url='https://www.chinapyg.com/plugin.php?id=dsu_paulsign:sign&infloat=yes&handlekey=dsu_paulsign&inajax=1&ajaxtarget=fwin_content_dsu_paulsign',
                     headers=header,
                     verify=False,
                     cookies=cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True),
                     # data=data,
                     timeout=5)
s = re.findall(r'<input type="hidden" name="formhash" value="(.*?)">', resp.text)  # 去掉style
print(s)
print(s[0])
# soup = BeautifulSoup(resp.text)

# print(soup)
# print(soup.find('input', attrs={'name': 'formhash', 'type': 'hidden'}).string)
