# !/usr/bin/python3
# -*- encoding:utf-8 -*-
'''
Description: 
Author: cj
Date: 2020-09-25 19:58:40
LastEditTime: 2020-09-26 11:05:53
LastEditors: cj
'''

import sys
import os
project_path = os.path.abspath(os.path.dirname(os.getcwd()))
path = project_path + "/src"
sys.path.append(path)
from gmcstore import Mysql 

if __name__ == '__main__':
    db = Mysql("localhost", 3306, "root", "c", "utf8")

    name = "u14045"
    uuid = "9a1e3f7d-18cc-0e96-a88a-2b09284d06f7"
    image_location = "/home/c/data/gmc_new_v2/test/xml/u14045.xml"
    image_hash = "20f653a4478e1385de61b394296fd167"

    name1 = "u140102"
    uuid1 = "9a1e3f7d-18cc-0e96-a88a-2b09284d06f7"
    image_location1 = "/home/c/data/gmc_new_v2/test/xml/u140402.xml"
    image_hash1 = "20f653a4478e1385de61b39429612345"

    # 判断插入
    db.insert_vm(name, uuid, image_location, image_hash)
    assert (db.is_vm_exist(name))

    db.insert_vm(name1, uuid1, image_location1, image_hash1)
    # assert (db.display_vm())
    # # #更新时间操作
    db.update_vm_time(name1, "delete_at")
    assert (db.get_value("name", name1, "deleted", "instance")[0] == 1)

    db.insert_vm(name1, uuid1, image_location1, image_hash1)
    # 更新和获取虚拟机状态操作
    db.update_vm_status(name, "active")
    assert (db.get_value_by_name(name, "vm_status")[0] == "active")

    # # #更新和获取虚拟机可信度操作
    db.update_vm_trusted(name, 1)
    assert (db.get_value_by_name(name, "trusted")[0] == "UnTrusted")

    #更新镜像位置操作
    db.update_vm_mirror_location(name, "/home/c/data/gmc/u14045.xml")
    assert (db.get_value_by_name(
        name, "mirror_location")[0] == "/home/c/data/gmc/u14045.xml")

    # 更新镜像hash操作
    db.update_vm_mirror_hash(name, "f03110bc49cfb705b9ced95607a9ec44")
    assert (db.get_value_by_name(
        name, "mirror_hash")[0] == "f03110bc49cfb705b9ced95607a9ec44")

    # 删除一个虚拟机
    db.delete_vm(name)
    assert (not db.is_vm_exist(name))

    # 删除所有虚拟机
    db.delete_vm_all()
    assert (not db.display_vm())
