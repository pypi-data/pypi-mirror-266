# -*- coding: utf-8 -*-
# @FileName  :uc_driver.py
# @Time      :2022/8/20 18:41
# @Author    :yaoys
# @Desc      : 调用浏览器
import io
import platform
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import undetected_chromedriver as uc


def get_driver_version(chrome_path=None):
    global cmd
    system = platform.system()

    if system == "Darwin":
        if chrome_path is None or len(str(chrome_path)) <= 0:
            cmd = r'''/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version'''
        else:
            cmd = r'''/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version'''
    elif system == "Windows":
        if chrome_path is None or len(str(chrome_path)) <= 0:
            cmd = r'''powershell -command "&{(Get-Item 'C:\Program Files\Google\Chrome\Application\chrome.exe').VersionInfo.ProductVersion}"'''
        else:
            cmd = r'''powershell -command "&{(Get-Item ''' + chrome_path + ''').VersionInfo.ProductVersion}"'''

    try:
        out, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    except IndexError as e:
        return 0

    if system == "Darwin":
        out = out.decode("utf-8").split(" ")[2].split(".")[0]
    elif system == "Windows":
        out = out.decode("utf-8").split(".")[0]

    return out


def get_driver(chrome_path=None):
    if chrome_path is None or len(chrome_path) <= 0:
        return None
    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")

    version = get_driver_version(chrome_path=chrome_path)
    if version == 0:
        raise Exception('open the chrome error, please check the chrome brower')
    driver = uc.Chrome(version_main=version, options=options)
    return driver


def close_driver(driver=None):
    if driver is None:
        raise Exception('The driver is None')

    driver.close()
    driver.quit()
