# !/usr/bin/env python3
# -*-coding:UTF-8 -*-
'''
Description: 执行tpm操作
Author: cj
Date: 2020-09-22 16:02:51
LastEditTime: 2020-09-26 13:46:32
LastEditors: cj
'''

import os
PATH = "/home/c/data/gmc_new_v3/src"


class Tpmop():
    def __init__(self, pcrn):
        self.pcrn = pcrn

    def pcr_extend(self, value):
        os.system('{path}/tpm_operation -p {pcrn} -v {value}'.format(
            path=PATH, pcrn=self.pcrn, value=value))

    def pcr_read(self):
        os.system('{path}/tpm_operation -g {pcrn}'.format(path=PATH,
                                                          pcrn=self.pcrn))


#if __name__ == "__main__":
#     to = Tpmop(12)
#     result = 1
#     # 获得历史值
#     to.pcr_read()
#     project_path = os.path.abspath(os.path.dirname(os.getcwd()))
#     path = project_path + "/Measure/history_pcr_value"
#     os.system("cat " + path)
#     # 扩展PCR
#     to.pcr_extend(result)
#     # 保存结果到度量列表
#     print("After pcr_extend:\n")
#     to.pcr_read()
#     os.system("cat " + path)
