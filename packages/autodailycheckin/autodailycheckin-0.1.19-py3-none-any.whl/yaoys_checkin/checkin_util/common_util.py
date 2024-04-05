import json
import os

from yaoys_checkin.checkin_util import file_type_json

# json配置文件：内容为各个平台的cookie和系统配置
__config_file_json_path__ = [
    "/ql/data/scripts/config/yaoys_checkin_config.json",
    "/ql/data/config/yaoys_checkin_config.json",
    "/ql/data/yaoys_checkin_config.json",
    "/ql/scripts/yaoys_checkin_config.json",
    "/ql/scripts/config/yaoys_checkin_config.json",
    "./config/yaoys_checkin_config.json",
    "./yaoys_checkin_config.json",
    "../config/yaoys_checkin_config.json"]
# json配置文件：内容为阿里云盘每日签到任务的任务详情
__config_aliyunpan_json_path__ = [
    "/ql/data/scripts/config/yaoys_aliyunpan_daily_task.json",
    "/ql/data/config/yaoys_aliyunpan_daily_task.json",
    "/ql/data/yaoys_aliyunpan_daily_task.json",
    "/ql/scripts/yaoys_aliyunpan_daily_task.json",
    "/ql/scripts/config/yaoys_aliyunpan_daily_task.json",
    "./config/yaoys_aliyunpan_daily_task.json",
    "./yaoys_aliyunpan_daily_task.json",
    "../config/yaoys_aliyunpan_daily_task.json"]


def print_message(is_print=True, message=None):
    if is_print and message is not None and len(message) > 0:
        print(str(message))


def get_config_file(file_type='json', config_type=0):
    '''
    file_type='json': 文件类型
    config_type：读取config目录下的哪一个配置文件，0：表示读取config目录下的系统配置文件，即包含cookie的文件，1：表示读取阿里云盘签到任务的配置文件
    '''
    config_file = None
    if file_type == file_type_json:
        json_file = open(get_config_path(file_type=file_type, config_type=config_type), encoding='utf-8', mode='r')
        config_file = json.load(json_file)
        json_file.close()

    return config_file


def get_config_path(file_type=None, config_type=0):
    if file_type is None:
        raise ValueError('参数错误，请联系管理员')
    config_path = None
    config_path_list = []
    config_path_array = None
    # 如果是json的配置文件
    if file_type == file_type_json:
        if config_type == 0:
            config_path_array = __config_file_json_path__
        elif config_type == 1:
            config_path_array = __config_aliyunpan_json_path__
        else:
            raise ValueError('config_type只能为0或者1')

    for one_path in config_path_array:
        _config_path = os.path.join(os.getcwd(), one_path)
        if os.path.exists(_config_path):
            config_path = os.path.normpath(_config_path)
            break
        config_path_list.append(os.path.normpath(os.path.dirname(_config_path)))

    if config_path is None:
        print(f"未找到 {config_path_array} 配置文件\n请在下方任意目录中添加「{config_path_array}」文件:\n" + "\n".join(config_path_list))
        raise FileNotFoundError(f"未找到 {config_path_array} 配置文件\n请在下方任意目录中添加「{config_path_array}」文件" + "\n".join(config_path_list))
    # print(config_path)
    return config_path
