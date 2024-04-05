# -*- coding: utf-8 -*-
# @FileName  :log_config.py
# @Time      :2023/3/31 21:30
# @Author    :yaoys
# @Desc      :

from yaoys_checkin.checkin_util import get_config_file
from yaoys_checkin.checkin_util.logutil import MY_LOG_INFO, getLogger


def get_checkin_logger(config_file=None, log_name='checkin_log'):
    if config_file is None:
        # print('读取配置文件')
        config_file = get_config_file()

    checkin_logger = None
    log_config = None

    if 'use_type' in config_file['common_config'] and config_file['common_config']['use_type'] == 0:
        # log_config = {
        #     'log_name': log_name,
        #     'log_level': MY_LOG_INFO,
        #     'save_log2_file': False
        # }
        # checkin_logger = getLogger(log_name=log_name,
        #                            log_level=MY_LOG_INFO,
        #                            save_log2_file=False)
        log_config = {
            'log_name': log_name,
            'log_path': '/ql/data/checkin_log',
            'log_level': MY_LOG_INFO,
            'save_log2_file': True,
            'is_only_file': True,
            'log_file_name': 'checkin_log',
            'is_split_log': False,
            'is_all_file': False
        }
        checkin_logger = getLogger(log_name=log_config['log_name'],
                                   log_path=log_config['log_path'],
                                   log_level=log_config['log_level'],
                                   save_log2_file=log_config['save_log2_file'],
                                   is_only_file=log_config['is_only_file'],
                                   log_file_name=log_config['log_file_name'],
                                   is_split_log=log_config['is_split_log'],
                                   is_all_file=log_config['is_all_file'])
    elif ('use_type' in config_file['common_config'] and config_file['common_config']['use_type'] == 1) or \
            ('use_type' in config_file['common_config'] and config_file['common_config']['use_type'] == 2):
        log_config = {
            'log_name': log_name,
            'log_path': '../checkin_log',
            'log_level': MY_LOG_INFO,
            'save_log2_file': True,
            'is_only_file': True,
            'log_file_name': 'checkin_log',
            'is_split_log': False,
            'is_all_file': False
        }
        checkin_logger = getLogger(log_name=log_config['log_name'],
                                   log_path=log_config['log_path'],
                                   log_level=log_config['log_level'],
                                   save_log2_file=log_config['save_log2_file'],
                                   is_only_file=log_config['is_only_file'],
                                   log_file_name=log_config['log_file_name'],
                                   is_split_log=log_config['is_split_log'],
                                   is_all_file=log_config['is_all_file'])
    else:
        print('use_type只能为0或者1')
        raise ValueError('use_type只能为0、1、2')

    if checkin_logger is None:
        print('log_config参数错误')
        raise ValueError('log_config参数错误')
    return checkin_logger, log_config
