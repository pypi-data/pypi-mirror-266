# -*- coding:UTF-8 -*-

"""
 @ProjectName  : PerformanceTest 
 @FileName     : log_file
 @Description  : 
 @Time         : 2024/1/5 17:29
 @Author       : Qredsun
 """
import os
import sys
import time

from loguru import logger
import logging

def init_log(file_path):
    # 处理 logging
    for hdlr in logging.root.handlers:
        logging.root.removeHandler(hdlr)

    logger.remove()

    handler_id = logger.add(sys.stderr, level="INFO")  # 添加一个可以修改控制的handler

    base_path = os.path.join(os.path.dirname(os.path.dirname(file_path)), 'log')
    os.makedirs(base_path,exist_ok=True)
    file_name = os.path.basename(file_path)[:-3]
    # 指定日志存放路径
    debug_log_path = os.path.join(base_path, time.strftime(f"%Y_%m_%d_%H-{file_name}-debug.log"))
    logger.add(debug_log_path, level="DEBUG")

    # debug_log_path = os.path.join(base_path, time.strftime(f"%Y_%m_%d_%H-{file_name}-info.log"))
    # logger.add(debug_log_path, level="INFO")

    # error_log_path = os.path.join(base_path, time.strftime(f"%y_%m_%d_%H-{file_name}-error.log"))
    # logger.add(error_log_path, level="ERROR")
    logging.root.addHandler(logger)
    return logger, base_path