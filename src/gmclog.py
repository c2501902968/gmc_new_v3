# !/usr/bin/env python3
# coding:utf-8
'''
Description: 日志模块
Author: cj
Date: 2020-09-22 15:07:49
LastEditTime: 2020-09-26 13:50:43
LastEditors: cj
'''

import time
import os
# from pathlib import Path
from loguru import logger

# project_path = Path.cwd()
# log_path = Path(project_path, "log")
project_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
log_path = project_path + "/log"
t = time.strftime("%Y_%m_%d")


class Loggings:
    __instance = None
    # 每一周创建一个新的日志
    logger.add("{log_path}/info-{time}.log".format(log_path=log_path, time=t),
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
               encoding="utf-8",
               enqueue=True,
               level='INFO',
               rotation="1 week")
    # 保留10天
    logger.add("{log_path}/debug-{time}.log".format(log_path=log_path, time=t),
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
               encoding="utf-8",
               enqueue=True,
               level='DEBUG',
               retention="5 days")
    logger.add("{log_path}/error-{time}.log".format(log_path=log_path, time=t),
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
               encoding="utf-8",
               enqueue=True,
               level='ERROR')

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Loggings, cls).__new__(cls, *args, **kwargs)

        return cls.__instance

    def info(self, msg):
        return logger.info(msg)

    def debug(self, msg):
        return logger.debug(msg)

    def warning(self, msg):
        return logger.warning(msg)

    def error(self, msg):
        return logger.error(msg)


# loggings = Loggings()
# if __name__ == '__main__':
#     loggings.info("中文test")
#     loggings.debug("中文test")
#     loggings.warning("中文test")
#     loggings.error("中文test")

#     logger.info('If you are using Python {}, prefer {feature} of course!',
#                 3.6,
#                 feature='f-strings')
#     n1 = "cool"
#     n2 = [1, 2, 3]
#     logger.info('If you are using Python {n1}, prefer {n2} of course!'.format(
#         n1=n1, n2=n2))
