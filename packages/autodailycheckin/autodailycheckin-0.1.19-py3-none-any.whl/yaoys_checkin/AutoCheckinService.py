#!/usr/bin/python
# !encoding:utf-8
'''
Author:xianqc
Date:2020-08-01
'''
# import os
# import sys
# import win32timezone
#
# import servicemanager
# import win32event
# import win32service
# import win32serviceutil
# from yaoysTools.log import getLogger, log_error, log_info
#
# from config.checkin_log_config import log_config
#
# logger = getLogger(log_name=str(os.path.basename(__file__)).split('.')[0],
#                    log_path=log_config['log_path'],
#                    log_level=log_config['log_level'],
#                    save_log2_file=log_config['save_log2_file'],
#                    is_only_file=log_config['is_only_file'],
#                    log_file_name=log_config['log_file_name'],
#                    is_split_log=log_config['is_split_log'],
#                    is_all_file=log_config['is_all_file'])
#
#
# class PythonService(win32serviceutil.ServiceFramework):
#     _svc_name_ = "Autocheckin_windows"  # 服务名
#     _svc_display_name_ = "Autocheckin_windows"  # 服务在windows系统中显示的名称
#     _svc_description_ = "每日自动签到"  # 服务的描述
#
#     def __init__(self, args):
#         win32serviceutil.ServiceFramework.__init__(self, args)
#         self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
#         self.run = True
#         self.start_scheduler = False
#         self.logger = logger
#
#     def SvcDoRun(self):
#         log_info("service is run....", my_logger=self.logger)
#         while self.run:
#             try:
#                 servicemanager.LogMsg(
#                     servicemanager.EVENTLOG_INFORMATION_TYPE,
#                     servicemanager.PYS_SERVICE_STARTED,
#                     (self._svc_name_, '')
#                 )
#                 if self.start_scheduler is False:
#                     self.start_checkin()
#                     log_info("auto checkin is running....", my_logger=self.logger)
#             except Exception as e:
#                 log_error(str(e), my_logger=self.logger)
#                 self.run = False
#
#     def SvcStop(self):
#         log_info("service is stop....", my_logger=self.logger)
#         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
#         win32event.SetEvent(self.hWaitStop)
#         self.run = False
#
#     def start_checkin(self):
#         from AutoCheckIn import start_checkin
#         log_info(' ** Starting checkin task ** ', my_logger=self.logger)
#         json_file_path = sys.argv[2]
#         if not os.path.exists(json_file_path):
#             log_error(sys.argv)
#             log_error(f'windows service error: json config is not exists,path: {json_file_path}', my_logger=self.logger)
#             raise Exception('json config is not exists')
#         else:
#             log_info(json_file_path, my_logger=self.logger)
#         start_checkin(sched=None, json_file_path=json_file_path)
#         self.start_scheduler = True
#
#
# # 使用下面的方式启动
# if __name__ == '__main__':
#     # json_file_path = os.path.abspath(os.path.dirname(sys.argv[0]) + os.path.sep + "..") + '/config/Config.json'
#     # if not os.path.exists(json_file_path):
#     #     log_error(os.path.abspath(os.path.dirname(sys.argv[0]) + os.path.sep + ".."), my_logger=logger)
#     #     log_error(f'windows service error: json config is not exists,path: {json_file_path}', my_logger=logger)
#     #     raise Exception('json config is not exists')
#     # else:
#     #     print('ok')
#     # log_info(sys.argv, my_logger=logger)
#     # log_info(len(sys.argv), my_logger=logger)
#     if len(sys.argv) == 1:
#         try:
#             evtsrc_dll = os.path.abspath(servicemanager.__file__)
#             # 如果修改过名字，名字要统一
#             servicemanager.PrepareToHostSingle(PythonService)
#             # 如果修改过名字，名字要统一
#             servicemanager.Initialize('PythonService', evtsrc_dll)
#             servicemanager.StartServiceCtrlDispatcher()
#         except Exception as details:
#             log_error(details, my_logger=logger)
#             import winerror
#
#             if details == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
#                 win32serviceutil.usage()
#     else:
#         # 如果修改过名字，名字要统一
#         win32serviceutil.HandleCommandLine(PythonService)
