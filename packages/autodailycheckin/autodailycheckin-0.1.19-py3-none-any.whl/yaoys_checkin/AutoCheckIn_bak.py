import functools
import os
import time

import func_timeout
from apscheduler.schedulers.blocking import BlockingScheduler

from yaoys_checkin.checkin_util import get_config_file, print_message
from yaoys_checkin.checkin_util.check_version_util import query_release_notes
from yaoys_checkin.checkin_util.checkin_class import checkin_class, message_class
from yaoys_checkin.checkin_util.logutil import log_error, log_info
from yaoys_checkin.checkin_util.checkin_log import get_checkin_logger

sched = None

config_json = get_config_file()
if config_json is None:
    raise Exception('配置文件错误')

checkin_logger, log_config = get_checkin_logger(config_file=config_json, log_name=str(os.path.basename(__file__)).split('.')[0])


def __get_sleep_count__():
    sleep_count = 5000
    for key, value in checkin_class.items():
        sleep_count = sleep_count + int(value['time_sleep']) + int(value['more_time_sleep'])
    return sleep_count


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                job_func(*args, **kwargs)
            except func_timeout.exceptions.FunctionTimedOut:
                import traceback
                # print(traceback.format_exc())
                # log_error('自定义异常: ' + str(traceback.format_exc()), my_logger=checkin_logger)
                log_error('自定义异常: 可忽略的异常,实现input自动结束', my_logger=checkin_logger)
                if sched is not None and cancel_on_failure:
                    sched.pause_job(job_id='checkin')
                else:
                    pass

        return wrapper

    return catch_exceptions_decorator


def checkin_task(task_name=None, config=None, cls_name=None, checkin_message=None, retry=None):
    if checkin_message is None:
        checkin_message = []
    message = []
    print_message(is_print=config['common_config']['is_print'], message='{} 开始执行任务 {} ....'.format('' if retry is False else '重试', task_name))
    if cls_name["cookie_name"] not in config['cookieOrUser']:
        checkin_message = f'配置文件中没有找到 *{cls_name["desc"]}*,请添加此项配置'
        return checkin_message
    message, is_success = cls_name["task_class_name"](config=config['cookieOrUser'][cls_name["cookie_name"]]['checkin_verification'], checkin_message=message, config_file=config_json, more_time_sleep=cls_name['more_time_sleep']).get_checkin_status()
    if cls_name['time_sleep'] > 0:
        time.sleep(cls_name['time_sleep'])
    if config['cookieOrUser'][cls_name["cookie_name"]]['push_message'] is True:
        checkin_message.append(message)
    print_message(is_print=config['common_config']['is_print'], message='{} 签到完毕, 签到信息:{}'.format(task_name, ''.join(message)))
    return checkin_message, is_success


def checkin_push_message(config=None, cls_name=None, checkin_message=None, retry=None):
    token = config['push_message'][cls_name[0]]
    if token is not None and str(token) != '':
        print_message(is_print=config['common_config']['is_print'], message='{} 推送签到信息至 {} ....'.format('' if retry is None else '尝试重新', cls_name[0]))
        if 'message_name' in config['push_message']:
            title = config['push_message']['message_name']
        else:
            title = 'checkin message'
        cls_name[1](token=token, title=title, checkin_message=checkin_message).send_message()
        print_message(is_print=config['common_config']['is_print'], message='推送签到信息至 {} 完毕'.format(cls_name[0]))


sleep_count = __get_sleep_count__()


@catch_exceptions(cancel_on_failure=False)
@func_timeout.func_set_timeout(sleep_count)
def checkin(**kwargs):
    config = get_config_file()
    if config is None:
        raise Exception('配置文件为空或者错误，请检查是否为正确的json文件')
    checkin_message = []
    if 'is_scheduler' in config['common_config'] and config['common_config']['is_scheduler'] is True:
        print('\n' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ': 定时任务的执行时间为： day_of_week=>{},hour=>{},minute=>{}'.format(config['scheduler']['timing_day_of_week'], config['scheduler']['timing_hour'], config['scheduler']['timing_minute']))
    print_message(is_print=config['common_config']['is_print'], message='\n##################################开始自动签到' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '##################################')
    log_info('##################################开始自动签到  ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '  ##################################', my_logger=checkin_logger)

    update_message = query_release_notes()
    log_info('版本检测：' + update_message, my_logger=checkin_logger)
    checkin_message.append('版本检测：' + update_message)
    checkin_message.append(f'总共需要签到的任务为')
    checkin_error_name = ''
    checkin_count = 0
    checkin_error_count = 0
    not_checkin_count = 0
    for task_name, cls_name in checkin_class.items():
        if 'is_used' in cls_name and cls_name['is_used'] is False:
            continue
        retry = False
        try:
            if task_name is None or len(str(task_name)) <= 0:
                log_info('*******************************任务名称为空*******************************\n', my_logger=checkin_logger)
                continue

            if cls_name is None:
                log_info('*******************************代码错误*******************************\n', my_logger=checkin_logger)
                continue
            # 配置文件中不存在该平台的相关配置
            if cls_name['cookie_name'] not in config['cookieOrUser']:
                checkin_message.append('{} 字段在配置文件*cookieOrUser*不存在，不执行该平台签到\n'.format(cls_name['cookie_name']))
                not_checkin_count += 1
                log_info('##################################{} 字段在配置文件*cookieOrUser*不存在，不执行该平台签到##################################'.format(cls_name['cookie_name']), my_logger=checkin_logger)
                continue

            # 不执行该平台签到
            if 'is_checkin' in config['cookieOrUser'][cls_name['cookie_name']] and config['cookieOrUser'][cls_name['cookie_name']]['is_checkin'] is False:
                checkin_message.append('[{}] 该平台不执行签到\n'.format(task_name))
                log_info('##################################{} 该平台不执行签到##################################'.format(task_name), my_logger=checkin_logger)
                not_checkin_count += 1
                continue

            # cookie 为空
            if 'checkin_verification' not in config['cookieOrUser'][cls_name['cookie_name']] or config['cookieOrUser'][cls_name['cookie_name']]['checkin_verification'] is None \
                    or str(config['cookieOrUser'][cls_name['cookie_name']]['checkin_verification']) == '':
                checkin_message.append('[{}] checkin_verification 字段不存在或者为空\n'.format(task_name))
                not_checkin_count += 1
                log_info('##################################{} checkin_verification 字段不存在或者为空##################################'.format(task_name), my_logger=checkin_logger)
                continue

            checkin_message, is_success = checkin_task(task_name=task_name, config=config, cls_name=cls_name, checkin_message=checkin_message, retry=retry)
            if is_success:
                checkin_count += 1
            else:
                checkin_error_name += cls_name['task_name'] + '、'
                checkin_error_count += 1
        except Exception as e:
            if retry is False:
                retry = True
                log_info('*******************************任务 {} 错误,开始重试 *******************************\n'.format(str(task_name)), my_logger=checkin_logger)
                checkin_message, is_success = checkin_task(task_name=task_name, config=config, cls_name=cls_name, checkin_message=checkin_message)
                if is_success:
                    checkin_count += 1
                else:
                    checkin_error_count += 1
            else:
                checkin_error_count += 1
                print_message(is_print=config['common_config']['is_print'], message='{} checkin error:'.format(task_name) + str(e))
                checkin_message.append('[{}] 签到错误，错误信息为: {} \n'.format(task_name, str(e)))
                log_info('*******************************{} 签到错误，错误信息为: {}*******************************\n'.format(task_name, str(e)), my_logger=checkin_logger)
        finally:
            continue

    # if len(checkin_error_name) > 0:
    #     checkin_message[1] = f'总共签到的任务个数为{checkin_count}个，不执行签到的任务数为{not_checkin_count}个,签到失败个数为{checkin_error_count}个,签到失败任务名称为:{checkin_error_name}\n'
    # else:
    checkin_message[1] = f'总共签到的任务个数为{checkin_count}个，不执行签到的任务数为{not_checkin_count}个,签到失败个数为{checkin_error_count}个\n'
    retry = False

    log_info('*******************************push message*******************************', my_logger=checkin_logger)
    if 'is_push_message' in config['push_message'] and config['push_message']['is_push_message'] is True:
        for key, value in message_class.items():
            cls_name = value
            message_name = key
            try:
                if key is None or len(str(key)) <= 0:
                    log_info('*******************************key is None*******************************\n', my_logger=checkin_logger)
                    continue

                if value is None:
                    log_info('*******************************推送消息配置类错误*******************************\n', my_logger=checkin_logger)
                    continue

                checkin_push_message(config=config, cls_name=cls_name, checkin_message=checkin_message)
            except Exception as e:
                if retry is False:
                    retry = True
                    log_info('*******************************重试推送消息 {}*******************************\n'.format(str(message_name)), my_logger=checkin_logger)
                    checkin_push_message(config=config, cls_name=cls_name, checkin_message=checkin_message)
                else:
                    print_message(is_print=config['common_config']['is_print'], message='{} 推送消息错误'.format(message_name) + str(e))
                    log_info('*******************************推送消息错误，错误信息为: {}*******************************\n'.format(str(e)), my_logger=checkin_logger)
            finally:
                continue
    else:
        log_info('不推送签到信息', my_logger=checkin_logger)
    log_info('*******************************推送消息完毕*******************************', my_logger=checkin_logger)
    log_info('###############################' + checkin_message[0].replace("\n", "") + '\t' + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())) + " 今日所有签到已结束" + '  ###################################', my_logger=checkin_logger)
    if config['common_config']['use_type'] == 1:
        input(checkin_message[0].replace('\n', '') + '\n' + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())) + " 今日所有签到已结束,输入任意字符结束，默认将在" + str(sleep_count) + '秒后自动结束')


def start_checkin(sched=None, json_file_path=None):
    try:
        day_of_week = config_json['scheduler']['timing_day_of_week']
        if day_of_week is None or len(day_of_week) <= 0:
            day_of_week = '0-6'
        hour = config_json['scheduler']['timing_hour']
        if hour is None or len(hour) <= 0:
            hour = '8'
        minute = config_json['scheduler']['timing_minute']
        if minute is None or len(minute) <= 0:
            minute = '0'

        # 如果是定时任务
        if 'is_scheduler' in config_json['common_config'] and config_json['common_config']['is_scheduler'] is True:
            print_message(is_print=config_json['common_config']['is_print'], message='\nThe timing config is: day_of_week=>{},hour=>{},minute=>{}'.format(day_of_week, hour, minute))
            log_info('The timing config is: day_of_week=>{},hour=>{},minute=>{}'.format(day_of_week, hour, minute), my_logger=checkin_logger)
            job_defaults = {
                'coalesce': True,
                'misfire_grace_time': None
            }
            if sched is None:
                sched = BlockingScheduler(job_defaults=job_defaults)
                sched.add_job(func=checkin,
                              trigger='cron',
                              id='checkin',
                              timezone='Asia/Shanghai',
                              day_of_week=day_of_week,
                              hour=hour,
                              minute=minute,
                              kwargs={'checkin_logger': checkin_logger, 'json_file_path': json_file_path, 'scheduler': sched},
                              max_instances=1)
                sched.start()
        # 如果不是定时任务，则立即执行一次签到
        else:
            checkin(json_file_path=json_file_path, checkin_logger=checkin_logger)
    except Exception as e:
        print_message(is_print=True, message=str(e))
        log_error(str(e), my_logger=checkin_logger)
        input("出现异常，请查看日志，输入任意字符结束")


if __name__ == '__main__':
    start_checkin(sched=sched)
