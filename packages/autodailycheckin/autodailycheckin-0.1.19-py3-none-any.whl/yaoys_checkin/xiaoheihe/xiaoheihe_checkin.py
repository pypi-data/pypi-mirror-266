# -*- coding: utf-8 -*-
# @FileName  :xiaoheihe_checkin.py
# @Time      :2023/7/5 18:06
# @Author    :yaoys
# @Desc      : 小黑盒签到,暂未完成
import os

from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.model.all_class_parent import allClassParent


class xiaoheihe(allClassParent):
    def __init__(self, **kwargs):
        super(xiaoheihe, self).__init__(**kwargs)

        # 交易猫链接配置
        self.JiaoYiMao_Api = "https://m.jiaoyimao.com"
        self.JiaoYiMao_Url = self.JiaoYiMao_Api + "/api2/account/integration/getMyIntegration"
        self.JiaoYiMao_SginUrl = self.JiaoYiMao_Api + "/api2/account/integration/signin"
        self.JiaoYiMao_Referer = self.JiaoYiMao_Api + "/account/integration/center?spm=gcmall.home2022.topshortcut.0"

        self.account_checkin_message = ''
        if self.logger is None:
            self.logger, log_config = get_checkin_logger(config_file=self.config_file, log_name=str(os.path.basename(__file__)).split('.')[0])

        self.checkin_message, self.is_success = self.xiaoheihe_sign()
        # self.get_checkin_message()

    def xiaoheihe_sign(self):
        return '', True
