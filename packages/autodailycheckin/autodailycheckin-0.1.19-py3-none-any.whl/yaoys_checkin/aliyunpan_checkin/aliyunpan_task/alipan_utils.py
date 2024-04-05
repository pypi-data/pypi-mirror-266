# -*- coding: utf-8 -*-
# @FileName  :utils.py
# @Time      :2024/2/11 13:39
# @Author    :yaoys
# @Desc      :
import hashlib
import random

import ecdsa
import requests

from yaoys_checkin.checkin_util.logutil import log_info


def random_hex(length):
    return ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for _ in range(length))


def get_signature(nonce, user_id, deviceId, appId=None):
    to_hex = lambda bytes: bytes.hex()
    to_u8 = lambda wordArray: wordArray.digest()

    sha256 = hashlib.sha256()
    sha256.update(user_id.encode('utf-8'))
    privateKey = sha256.digest()

    curve = ecdsa.SECP256k1
    signing_key = ecdsa.SigningKey.from_string(privateKey, curve=curve)
    verifying_key = signing_key.get_verifying_key()
    publicKey = '04' + verifying_key.to_string().hex()
    if appId is None:
        appId = random_hex(16)
    to_sign = f"{appId}:{deviceId}:{user_id}:{nonce}".encode('utf-8')
    signature = signing_key.sign(to_sign, hashfunc=hashlib.sha256)
    signature = signature.hex() + '01'

    return {'signature': signature, 'publicKey': publicKey}


def create_device_session(
        user_id,
        accesstoken,
        deviceId,
        refreshToken,
        pubKey,
        signature=None,
        deviceName=None,
        modelName=None,
        x_canary=None,
        user_agent=None,
        logger=None
):
    if signature is None:
        signature = get_signature(nonce=1, user_id=user_id, deviceId=deviceId)['signature']

    if pubKey is None:
        pubKey = random_hex(32)

    if refreshToken is None:
        return False, None

    if deviceName is None or modelName is None or x_canary is None or user_agent is None:
        return False, None
    result = None
    try:
        result = requests.post(
            'https://api.alipan.com/users/v1/users/device/create_session',
            json={
                'deviceName': deviceName,
                'modelName': modelName,
                'nonce': '0',
                'pubKey': pubKey,
                'refreshToken': refreshToken,
            },
            headers={
                'content-type': 'application/json;charset=UTF-8',
                'referer': 'https://alipan.com/',
                'origin': 'https://alipan.com/',
                'x-canary': x_canary,
                'user-agent': user_agent,
                'x-device-id': deviceId,
                'authorization': f'Bearer {accesstoken}',
                'x-signature': signature
            },
        )
        if result is not None and result.status_code == 200 \
                and 'result' in result.json() and 'success' in result.json() \
                and result.json()['result'] is True and result.json()['success'] is True:
            # log_info('时光设备间任务，请查看日志333', my_logger=logger)
            return True, {"deviceId": deviceId, "pubKey": pubKey, "signature": signature}
        else:
            # log_info('创建虚拟设备出现错误,result: ' + result, my_logger=logger)
            return False, result
    except Exception as e:
        # log_info('创建虚拟设备出现错误,请查看日志: ' + str(e) + ", " + result, my_logger=logger)
        return False, str(e)


def device_logout(deviceId, accesstoken):
    result = requests.post('https://api.aliyundrive.com/users/v1/users/device_logout', headers={
        'x-device-id': deviceId,
        'authorization': f'Bearer {accesstoken}',
    }).json()
    if 'result' in result and 'success' in result and result['result'] is True and result['success'] is True:
        return True
    else:
        return False
