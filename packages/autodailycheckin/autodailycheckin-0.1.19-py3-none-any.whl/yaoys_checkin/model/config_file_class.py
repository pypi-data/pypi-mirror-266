import json
from types import SimpleNamespace

from yaoys_checkin.checkin_util import get_config_path
from yaoys_checkin.model.cookieOrUser_class import able_sci, bilibili_icon, bilibili_live


# https://blog.csdn.net/fengyuyeguirenenen/article/details/129077547
# https://www.cnblogs.com/alxed/p/14748080.html

class common_config(object):
    def __init__(self, is_print: bool = None, is_scheduler: bool = None, use_type: int = None):
        self.is_print = is_print
        self.is_scheduler = is_scheduler
        self.use_type = use_type


class scheduler(object):
    def __init__(self, timing_day_of_week: str = None, timing_hour: str = None, timing_minute: str = None):
        self.timing_day_of_week = timing_day_of_week
        self.timing_hour = timing_hour
        self.timing_minute = timing_minute


class cookieOrUser(object):
    def __init__(self, able_sci_class: able_sci = None,
                 bilibili_live_class: bilibili_live = None,
                 bilibili_icon_class: bilibili_icon = None):
        self.able_sci_class = able_sci_class
        self.bilibili_live_class = bilibili_live_class
        self.bilibili_icon_class = bilibili_icon_class


class push_message(object):
    def __init__(self, is_push_message: bool = None, message_name: str = None, pushPlus: str = None, server: str = None):
        self.is_push_message = is_push_message
        self.message_name = message_name
        self.pushPlus = pushPlus
        self.server = server


class yaoys_config_file(object):
    def __init__(self, common_configs: common_config = None, schedulers: scheduler = None, cookieOrUsers: cookieOrUser = None, push_messages: push_message = None):
        self.common_config = common_configs
        self.scheduler = schedulers
        self.cookieOrUser = cookieOrUsers
        self.push_message = push_messages


class parseJson2Class(object):
    def __init__(self):
        self.config_class = yaoys_config_file
        self.parse_json2Class()

    def parse_json2Class(self):
        json_file = open(get_config_path(file_type='json', config_type=0), encoding='utf-8', mode='r')
        #
        json_str = json.load(json_file, object_hook=lambda d: SimpleNamespace(**d))
        json_file.close()
        self.config_class = json_str

        # result = self.config_class()
        # result.__dict__ = json_str
        # self.config_class = result

    def get_config(self):
        if self.config_class is None:
            self.parse_json2Class()
        return self.config_class
