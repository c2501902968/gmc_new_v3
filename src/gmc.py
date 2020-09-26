'''
Description: gmc的管理模块
Author: cj
Date: 2020-09-23 10:32:33
LastEditTime: 2020-09-26 11:21:05
LastEditors: cj
'''
# !/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import gmcstore as gsql
import gmclog as glog
import gmcfile as gfile1
import gmcattest as gattest1
import gmctpm as gtpm1

XML_FILE_PATH = "/etc/libvirt/qemu/"
#XML_FILE_PATH = "/home/c/data/gmc_new_v3/test/xml"
XML_GUEST_NAME = "name"
XML_PATH = "source"
XML_SUBPATH = "file"
XML_UUID = "uuid"

db = gsql.Mysql("localhost", 3306, "root", "c", "utf8")
logger = glog.Loggings()
file = gfile1.File()


def define(guest_name, operation):
    '''
    define操作的作用：
    根据guest_name判断数据库是否存在该虚拟机
    不存在：
        创建虚拟机，向数据库里添加信息
            guest_name:---> xml文件
            guest_uuid:---> 从xml文件中读取uuid
            mirror_location: ---> 从xml文件中读取镜像位置
            mirror_hash: ---> 根据镜像位置计算hash值
        插入虚拟机
        更新虚拟机的状态为define，不更新其实也行，因为，创建成功后，就会启动，虚拟机的状态会变成running
    存在，则失败
    todo：有个疑问：
    1 此时的mirror是不是基础镜像的值啊？
    2 马上就启动了，还需要进行校验么？
    3 考虑一种情况，那就是，当基础镜像已经在本地很久了，那么在创建时应该是要校验一下的。
    '''
    if not db.is_vm_exist(guest_name):
        logger.debug("start: %s doesn't exist,insert it into instance" %
                     guest_name)
        # print(XML_PATH)
        xml_file_list = file.get_xml_file_list(XML_FILE_PATH)
        # print(xml_file_list)
        guest_xml = file.find_guest_xml(xml_file_list, guest_name)
        # uuid
        guest_uuid = file.get_xml_content(guest_xml, XML_UUID)
        # mirror_location
        mirror_location = file.get_xml_content(guest_xml, XML_PATH,
                                               XML_SUBPATH)
        # mirror_hash
        mirror_hash = file.get_file_md5(mirror_location)
        db.insert_vm(guest_name, guest_uuid, mirror_location, mirror_hash)
        db.update_vm_status(guest_name, operation)
        logger.info(
            "define: Name:{name}, Uuid:{uuid}, mirror_location:{location}, mirror_hash:{hash}"
            .format(name=guest_name,
                    uuid=guest_uuid,
                    location=mirror_location,
                    hash=mirror_hash))
    else:
        logger.error("%s exists! you can't define it again" % guest_name)


def start(guest_name, operation):
    '''
    start操作的作用：开启虚拟机
    判断是否存在该虚拟机：
    存在：
        则进行验证，且更新虚拟机的状态和update_at时间，
        将验证结果存储到度量列表，及扩展值到PCR12中
    否则：
        不存在该虚拟机启动失败
    '''
    if db.is_vm_exist(guest_name):
        att = gattest1.Attest(guest_name)
        tpmop = gtpm1.Tpmop(12)
        result = att.check_image_hash()
        # 获得历史值-history_pcr_value
        tpmop.pcr_read()
        # 扩展PCR
        tpmop.pcr_extend(result)
        logger.debug("extend PCR 12 with value {value}".format(value=result))
        # 保存结果到度量列表--measurelist
        file.write_measure_list(
            "guest_name:{name} trusted:{trusted} \n".format(name=guest_name,
                                                            trusted=result))
        logger.debug("add guest_name:{name} trusted:{trusted}".format(
            name=guest_name, trusted=result))

        db.update_vm_trusted(guest_name, result)
        db.update_vm_status(guest_name, operation)
        db.update_vm_time(guest_name, "update_at")
        logger.info("start: {name}".format(name=guest_name))
    else:
        logger.error(
            "{name} doesn't exist! you can't start it".format(name=guest_name))


def stopped(guest_name, operation):
    '''
    stop操作作用：关闭虚拟机
    1 更新虚拟机镜像的hash值
    2 根据guest_name 更新虚拟机的状态为stopped
    3 根据guest_name 更新虚拟机的update_at
    '''
    att = gattest1.Attest(guest_name)
    att.update_hash()
    db.update_vm_status(guest_name, operation)
    db.update_vm_time(guest_name, "update_at")
    logger.info("{name} has been stopped! ".format(name=guest_name))


def undefine(guest_name, operation):
    '''
    undefine操作的作用：删除虚拟机
    1 更新虚拟机的"deleted_at"
    2 更新虚拟机的状态为 undefine
    注意：todo：这里并没有从数据库里把数据删除~
    '''
    db.update_vm_status(guest_name, operation)
    db.update_vm_time(guest_name, "delete_at")
    logger.info("{name} has been deleted!".format(name=guest_name))


def started(guest_name):
    '''
    started: 虚拟机已经运行了
    1 更新虚拟机的状态为running
    '''
    db.update_vm_status(guest_name, "running")
    logger.info("{name} is running".format(name=guest_name))


if __name__ == "__main__":

    guest_name = sys.argv[1]
    operation = sys.argv[2]

    if operation == "prepare":
        # 在libvirt执行任何资源标记之前（XML中定义的label）
        pass
    elif operation == "start":
        # 在libvirt完成标记所有的资源之后，但是还没有启动guest
        start(guest_name, operation)
        # start(guest_name)
    elif operation == "started":
        # 在QEMU虚拟机成功启动之后
        started(guest_name)
    elif operation == "stopped":
        # 当QEMU guest停止时，在libvirt恢复任何标记(label)之前
        stopped(guest_name, operation)
        # stop(guest_name)
    elif operation == "release":
        # 在libvirt释放所有资源之后
        pass
    elif operation == "define":
        # 在libvirt创建虚拟机前
        define(guest_name, operation)

    elif operation == "undefine":
        # 在libvirt删除虚拟机之后
        undefine(guest_name, operation)
    elif operation == "migrate":
        # 在即将到来的迁移之前
        pass
    elif operation == "reconnect":
        # 当libvirtd daemon重启并且重新连接到之前的正在运行的QEMU进程时
        pass
    elif operation == "attach":
        # 当QEMU驱动附加到已经启动的QEMU进程时
        pass
    else:
        logger.error("sorry, don't have operation: {op}".format(op=operation))
