# -*- coding: utf-8 -*-
# @FileName  :AutoCheckIn2.py
# @Time      :2023/8/5 19:39
# @Author    :yaoys
# @Desc      :
import datetime
import functools
import os
import random
import sys
import time

import func_timeout
from apscheduler.schedulers.blocking import BlockingScheduler

from yaoys_checkin.checkin_util import checkin_class, get_config_file, message_class, print_message
from yaoys_checkin.checkin_util.check_version_util import query_release_notes
from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger
from yaoys_checkin.checkin_util.logutil import log_error, log_info

sleep_count = 5000
logger = None


# 超时报错
def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                job_func(*args, **kwargs)
            except func_timeout.exceptions.FunctionTimedOut:
                import traceback
                # log_error('自定义异常: ' + str(traceback.format_exc()), my_logger=checkin_logger)
                log_error('自定义异常: 可忽略的异常,实现input自动结束', my_logger=logger)
                # if scheduler is not None and cancel_on_failure:
                #     scheduler.pause_job(job_id='checkin')

        return wrapper

    return catch_exceptions_decorator


def __get_config_json__():
    # 配置文件
    config_json = get_config_file()
    if config_json is None:
        raise Exception('配置文件错误')

    return config_json


class Autochekin(object):
    def __init__(self):

        # 获取配置文件
        self.config_json = __get_config_json__()
        # log日志，log日志配置
        self.checkin_logger, self.log_config = get_checkin_logger(config_file=self.config_json, log_name=str(os.path.basename(__file__)).split('.')[0])
        # 初始化休眠时间总数
        self.sleep_count = 5000
        # 出现异常自动停止任务
        self.cancel_on_failure = False
        # 定时任务
        self.scheduler = None
        # 定时任务id
        self.scheduler_id = "checkin"
        # 任务名称
        self.task_name = None
        # 配置类checkin_class中的json中的value值
        self.cls_name = None
        # 是否重试
        self.retry = None
        # 签到信息
        self.checkin_message = None
        # 初始化超时时间
        self.__get_sleep_count__()
        #     线程池中的线程
        self.thread_list = []

    # 获取休眠总数
    def __get_sleep_count__(self):
        for key, value in self.config_json.items():
            if key != 'cookieOrUser':
                continue
            for key1, value1 in value.items():
                if 'more_time_sleep' in value1:
                    self.sleep_count += value1['more_time_sleep']
                if 'time_sleep' in value1:
                    self.sleep_count += value1['time_sleep']

    def checkin_task(self):
        if self.checkin_message is None:
            self.checkin_message = []
        message = []
        print_message(is_print=self.config_json['common_config']['is_print'],
                      message='{} 开始执行任务 {} ....'.format('' if self.retry is False else '重试', self.task_name))
        if self.cls_name["cookie_name"] not in self.config_json['cookieOrUser']:
            checkin_message = f'配置文件中没有找到 *{self.cls_name["desc"]}*,请添加此项配置'
            return checkin_message, False, self.task_name

        more_time_sleep = 0
        time_sleep = 0
        if 'more_time_sleep' in self.config_json['cookieOrUser'][self.cls_name["cookie_name"]]:
            more_time_sleep = self.config_json['cookieOrUser'][self.cls_name["cookie_name"]]['more_time_sleep']
        if 'time_sleep' in self.config_json['cookieOrUser'][self.cls_name["cookie_name"]]:
            time_sleep = self.config_json['cookieOrUser'][self.cls_name["cookie_name"]]['time_sleep']
        message, is_success = self.cls_name["task_class_name"](
            checkin_verification=self.config_json['cookieOrUser'][self.cls_name["cookie_name"]]['checkin_verification'],
            checkin_message=message,
            config_file=self.config_json,
            more_time_sleep=more_time_sleep,
            time_sleep=time_sleep).get_checkin_status()
        # if self.config_json['cookieOrUser'][self.cls_name["cookie_name"]]['push_message'] is True:
        #     self.checkin_message.append(message)
        print_message(is_print=self.config_json['common_config']['is_print'], message='{} 签到完毕, 签到信息:{}'.format(self.task_name, ''.join(message)))
        return message, is_success, self.task_name

    def checkin_push_message(self):
        token = self.config_json['push_message'][self.cls_name[0]]
        if token is not None and str(token) != '':
            print_message(is_print=self.config_json['common_config']['is_print'], message='{} 推送签到信息至 {} ....'.format('' if self.retry is False else '尝试重新', self.cls_name[0]))
            if 'message_name' in self.config_json['push_message']:
                title = self.config_json['push_message']['message_name']
            else:
                title = 'checkin message'
            message = self.cls_name[1](token=token, title=title, checkin_message=self.checkin_message).send_message()
            print_message(is_print=self.config_json['common_config']['is_print'], message='推送签到信息至 {} 完毕'.format(self.cls_name[0]))

    def start_checkin(self):
        try:
            # 如果是定时任务
            if 'is_scheduler' in self.config_json['common_config'] and self.config_json['common_config']['is_scheduler'] is True:
                day_of_week = self.config_json['scheduler']['timing_day_of_week']
                if day_of_week is None or len(day_of_week) <= 0:
                    day_of_week = '0-6'
                hour = self.config_json['scheduler']['timing_hour']
                if hour is None or len(hour) <= 0:
                    hour = '8'
                minute = self.config_json['scheduler']['timing_minute']
                if minute is None or len(minute) <= 0:
                    minute = '0'
                print_message(is_print=self.config_json['common_config']['is_print'], message='\nThe timing config is: day_of_week=>{},hour=>{},minute=>{}'.format(day_of_week, hour, minute))
                log_info('The timing config is: day_of_week=>{},hour=>{},minute=>{}'.format(day_of_week, hour, minute),
                         my_logger=self.checkin_logger)
                job_defaults = {
                    'coalesce': True,
                    'misfire_grace_time': None,
                    "timezone": 'Asia/Shanghai',
                    "max_instances": 1
                }
                if self.scheduler is None:
                    sched = BlockingScheduler(job_defaults=job_defaults)
                    self.scheduler = sched

                    self.scheduler.add_job(func=self.checkin,
                                           trigger='cron',
                                           id=self.scheduler_id,
                                           # timezone='Asia/Shanghai',
                                           day_of_week=day_of_week,
                                           hour=hour,
                                           minute=minute,
                                           kwargs={"scheduler": self.scheduler, "day_of_week": day_of_week}
                                           # max_instances=1
                                           )

                    self.scheduler.start()
            # 如果不是定时任务，则立即执行一次签到
            else:
                self.checkin()
                # raise ValueError('非定时任务,服务启动执行一次签到结束')
                input("非定时任务,服务启动执行一次签到结束")
        except Exception as e:
            print_message(is_print=True, message=str(e))
            log_info(str(e), my_logger=self.checkin_logger)
            sys.exit()

    def judge_is_checkin(self, not_checkin_count):
        # checkin_class中is_used字段为False，不执行签到
        if 'is_used' in self.cls_name and self.cls_name['is_used'] is False:
            return False
        if self.task_name is None or len(str(self.task_name)) <= 0:
            log_info('*******************************任务名称为空*******************************\n', my_logger=self.checkin_logger)
            not_checkin_count += 1
            return False

        if self.cls_name is None:
            log_info('*******************************代码错误*******************************\n', my_logger=self.checkin_logger)
            not_checkin_count += 1
            return False
        # 配置文件中不存在该平台的相关配置
        if self.cls_name['cookie_name'] not in self.config_json['cookieOrUser']:
            self.checkin_message.append('{} 字段在配置文件*cookieOrUser*不存在，不执行该平台签到\n'.format(self.cls_name['cookie_name']))
            not_checkin_count += 1
            log_info('##################################{} 字段在配置文件*cookieOrUser*不存在，不执行该平台签到##################################'.format(self.cls_name['cookie_name']), my_logger=self.checkin_logger)
            return False

        # 不执行该平台签到
        if 'is_checkin' in self.config_json['cookieOrUser'][self.cls_name['cookie_name']] and \
                self.config_json['cookieOrUser'][self.cls_name['cookie_name']]['is_checkin'] is False:
            self.checkin_message.append('[{}] 该平台不执行签到\n'.format(self.task_name))
            log_info('##################################{} 该平台不执行签到##################################'.format(self.task_name), my_logger=self.checkin_logger)
            not_checkin_count += 1
            return False

        # cookie 为空
        if 'checkin_verification' not in self.config_json['cookieOrUser'][self.cls_name['cookie_name']] or \
                self.config_json['cookieOrUser'][self.cls_name['cookie_name']]['checkin_verification'] is None \
                or str(self.config_json['cookieOrUser'][self.cls_name['cookie_name']]['checkin_verification']) == '':
            self.checkin_message.append('[{}] checkin_verification 字段不存在或者为空\n'.format(self.task_name))
            not_checkin_count += 1
            log_info('##################################{} checkin_verification 字段不存在或者为空##################################'.format(self.task_name), my_logger=self.checkin_logger)
            return False

    @catch_exceptions(cancel_on_failure=False)
    @func_timeout.func_set_timeout(sleep_count)
    def checkin(self, **kwargs):

        # 每次执行重新读取获取配置文件，以便于修改配置文件内容后不需要重启

        self.config_json = __get_config_json__()

        # 每次执行初始化参数
        self.checkin_message = []
        self.thread_list = []
        if 'is_scheduler' in self.config_json['common_config'] and self.config_json['common_config']['is_scheduler'] is True:
            print('\n' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ': 定时任务的执行时间为： day_of_week=>{},hour=>{},minute=>{}'.format(
                self.config_json['scheduler']['timing_day_of_week'], self.config_json['scheduler']['timing_hour'], self.config_json['scheduler']['timing_minute']))
        print_message(is_print=self.config_json['common_config']['is_print'], message='\n##################################开始自动签到' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '##################################')
        log_info('##################################开始自动签到  ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '  ##################################', my_logger=self.checkin_logger)

        update_message = query_release_notes()
        log_info('版本检测：' + update_message, my_logger=self.checkin_logger)
        self.checkin_message.append('版本检测：' + update_message)
        self.checkin_message.append(f'总共需要签到的任务为')
        checkin_error_name = ''
        checkin_count = 0
        checkin_error_count = 0
        not_checkin_count = 0
        if 'thread_num' in self.config_json['common_config']:
            thread_num = self.config_json['common_config']['thread_num']
        else:
            thread_num = 15
        time_start = time.perf_counter()

        for task_name, cls_name in checkin_class.items():
            try:
                self.task_name = task_name
                self.cls_name = cls_name
                self.retry = False
                # 判断是否执行该平台签到
                if self.judge_is_checkin(not_checkin_count=not_checkin_count) is False:
                    continue

                checkin_message, is_success, task_name = self.checkin_task()
                if self.config_json['cookieOrUser'][task_name]['push_message'] is True:
                    self.checkin_message.append(checkin_message)
                if is_success:
                    checkin_count += 1
                else:
                    checkin_error_name += self.cls_name['task_name'] + '、'
                    checkin_error_count += 1
            except Exception as e:
                if self.retry is False:
                    self.retry = True
                    checkin_message, is_success, task_name = self.checkin_task()
                    if self.config_json['cookieOrUser'][task_name]['push_message'] is True:
                        self.checkin_message.append(checkin_message)
                    if is_success:
                        checkin_count += 1
                    else:
                        checkin_error_name += self.cls_name['task_name'] + '、'
                        checkin_error_count += 1
                else:
                    checkin_error_count += 1
                    print_message(is_print=self.config_json['common_config']['is_print'], message='{} checkin error:'.format(self.task_name) + str(e))
                    self.checkin_message.append('[{}] 签到错误，错误信息为: {} \n'.format(self.task_name, str(e)))
                    log_info('*******************************{} 签到错误，错误信息为: {}*******************************\n'.format(self.task_name, str(e)), my_logger=self.checkin_logger)
            finally:
                continue

        total_time = time.perf_counter() - time_start

        hour = random.randint(7, 10)
        minute = random.randint(0, 59)
        day_of_week = kwargs.get("day_of_week", "0-6")
        next_run_time = None
        if "random_scheduler_time_hour" in self.config_json["scheduler"] \
                and isinstance(self.config_json["scheduler"]["random_scheduler_time_hour"], list) \
                and self.config_json['common_config']['is_scheduler'] is True \
                and self.config_json['scheduler']['random_scheduler_time'] is True:
            hour = random.choice(self.config_json["scheduler"]["random_scheduler_time_hour"])

        # 开启了随机时间和是定时任务
        if self.config_json['common_config']['is_scheduler'] is True \
                and self.config_json['scheduler']['random_scheduler_time'] is True:
            if self.scheduler is not None:
                temp_dict = {
                    "timezone": 'Asia/Shanghai'
                }
                temp_trigger = self.scheduler._create_trigger(trigger='cron', trigger_args=temp_dict)
                next_run_time = temp_trigger.get_next_fire_time(None, datetime.datetime.strptime('{} {}:{}:{}'.format(datetime.datetime.now().strftime("%Y-%m-%d"), hour, minute, 0), '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=1, hours=0,
                                                                                                                                                                                                                                minutes=0))
                self.scheduler.modify_job(job_id=self.scheduler_id, trigger=temp_trigger, next_run_time=next_run_time)
                log_info("修改下次执行时间成功", my_logger=self.checkin_logger)
        self.checkin_message[1] = f'总共签到的任务个数为{checkin_count}个，不执行签到的任务数为{not_checkin_count}个,签到失败个数为{checkin_error_count}个,总时间为{total_time},下次执行签到时间为: {next_run_time}\n'
        self.retry = False

        log_info('*******************************push message*******************************', my_logger=self.checkin_logger)
        if 'is_push_message' in self.config_json['push_message'] and self.config_json['push_message']['is_push_message'] is True:
            for key, value in message_class.items():
                self.cls_name = value
                try:
                    if key is None or len(str(key)) <= 0:
                        log_info('*******************************系统异常，消息配置名称为空*******************************\n', my_logger=self.checkin_logger)
                        continue

                    if value is None:
                        log_info('*******************************系统异常，推送消息配置类错误*******************************\n', my_logger=self.checkin_logger)
                        continue
                    if self.config_json['push_message'][self.cls_name[0]] is None or len(self.config_json['push_message'][self.cls_name[0]]) <= 0:
                        continue

                    self.checkin_push_message()
                except Exception as e:
                    if self.retry is False:
                        self.retry = True
                        log_info('*******************************重试推送消息 {},当前错误为 {}*******************************\n'.format(str(key), str(e)), my_logger=self.checkin_logger)
                        time.sleep(1)
                        self.checkin_push_message()
                    else:
                        print_message(is_print=self.config_json['common_config']['is_print'], message='{} 推送消息错误'.format(key) + str(e))
                        log_info('*******************************推送消息错误，错误信息为: {}*******************************\n'.format(str(e)), my_logger=self.checkin_logger)
                finally:
                    continue
        else:
            log_info('不推送签到信息', my_logger=self.checkin_logger)
        log_info('*******************************推送消息完毕*******************************', my_logger=self.checkin_logger)
        log_info('###############################' + self.checkin_message[0].replace("\n", "") + '\t' + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())) + " 今日所有签到已结束" + '  ###################################',
                 my_logger=self.checkin_logger)

        if self.config_json['common_config']['use_type'] == 1:
            input(self.checkin_message[0].replace('\n', '') + '\n' + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())) + " 今日所有签到已结束,输入任意字符结束，默认将在" + str(sleep_count) + '秒后自动结束')


def main():
    autocheckin = Autochekin()
    global sleep_count
    sleep_count = autocheckin.sleep_count
    global logger
    logger = autocheckin.checkin_logger
    autocheckin.start_checkin()


if __name__ == '__main__':
    main()
