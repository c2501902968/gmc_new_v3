'''
Description: 文件相关操作
Author: cj
Date: 2020-09-22 19:37:22
LastEditTime: 2020-09-26 14:10:28
LastEditors: cj
'''
# !/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import time
import hashlib
# import gmc_new_v2.gmclog as log
import gmclog as log
import xml.etree.ElementTree as ET
# import libxml2

XML_GUEST_NAME = "name"
logger = log.Loggings()


class File():
    def __init__(self, res=[]):
        self.res = res

    def get_file_md5(self, filename):
        '''
        description: 对文件进行md5加密
        param : filename:文件的名字
        return:文件的md5的hash值
        '''
        if not os.path.isfile(filename):
            return
        myhash = hashlib.md5()
        f = open(filename, 'rb')
        while True:
            b = f.read(8096)
            if not b:
                break
            myhash.update(b)
        f.close()
        #logger.debug("%s md5: %s" % (filename, myhash.hexdigest()))
        return myhash.hexdigest()

    def get_xml_file_list(self, path):
        '''
        description: 获取path路径下该文件及其子文件夹下的所有xml文件
        param : path:xml文件的路径
        return :xml文件列表
        '''
        xml_file_list = []
        for dirpath, dirnames, filenames in os.walk(path):
            for file in filenames:
                if os.path.splitext(file)[1] == '.xml':
                    xml_file_list.append(os.path.join(dirpath, file))
        logger.debug("list xml file under %s : %s" % (path, xml_file_list))
        return xml_file_list

    def get_xml_content(self, xml, path, subpath=None):
        '''
        description:  获取xml文件里定义的某一个label的内容
        param: path：xml的标签，subpath ：标签的子内容
        return： xml的path(/subpath)的内容
        '''
        try:
            # print(xml)
            doc = ET.parse(xml)
            root = doc.getroot()
            for child in root.iter(path):
                if subpath:
                    res = child.attrib.get(subpath)
                else:
                    res = child.text
                if res:
                    logger.debug(
                        "xml:{xml} path: {path}/{subpath} value:{value}".
                        format(xml=xml, path=path, subpath=subpath, value=res))
                    return res

        except (ET.ParseError, TypeError):
            logger.error("Error: get_xml_content fail")
            return

    def get_file_name(self, filename):
        '''
        description: 在filename（绝对路径）中获取文件名字
        param:filename:（绝对路径）
        return: 文件名
        '''
        (filepath, tempfilename) = os.path.split(filename)
        logger.debug("%s filename: %s" % (filename, tempfilename))
        return tempfilename

    def find_guest_xml(self, xml_file_list, guest_name):
        '''
        description: 根据guest_name找到相应的xml文件
        param :
            xml_file_list:xml文件列表
            guest_name:虚拟机名字
        return: 得到对应的xml文件
        '''
        for xml in xml_file_list:
            name = self.get_xml_content(xml, XML_GUEST_NAME)
            # print(name)
            if name == guest_name:
                guest_xml = xml
                # print xml
                logger.debug(" %s xml file is %s" % (guest_name, guest_xml))
                return guest_xml

    def write_measure_list(self, value):
        '''
        description: 将值添加到度量列表
        '''
        path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        folder = path + '/Measure/'
        if not os.path.exists(folder):
            os.mkdir(folder) 
        file_name = folder + 'MeasureList'
        f = open(file_name, "a+")
        f.write(time.strftime("%Y-%m-%d %H:%M:%S \t", time.localtime()))
        f.write(value)
        f.close()
if __name__ == "__main__":
    file = File()
    file.write_measure_list("hhah\n")


