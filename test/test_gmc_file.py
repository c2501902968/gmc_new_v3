# !/usr/bin/python3
# -*- encoding:utf-8 -*-
'''
Description: gmcfile的测试文件
Author: cj
Date: 2020-09-25 14:58:25
LastEditTime: 2020-09-26 14:08:28
LastEditors: cj
'''
import unittest

import sys
import os

project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
path = project_path + "/src"
sys.path.append(path)
print(path)
# sys.path.append("/home/c/data/gmc_new_v3/src")
import gmcfile as gfile1

file = gfile1.File()


class TestGmcFile(unittest.TestCase):
    def test_get_xml_file_list(self):
        self.assertEqual(file.get_xml_file_list("xml"),
                         ['xml/u140402.xml', 'xml/u14045.xml'])

    def test_find_guest_xml(self):
        xml_list = ['xml/u140402.xml', 'xml/u14045.xml']
        self.assertEqual(file.find_guest_xml(xml_list, "u14045"),
                         "xml/u14045.xml")

    def test_get_file_name(self):
        self.assertEqual(file.get_file_name("xml/u14045.xml"), "u14045.xml")

    def test_get_xml_content(self):
        self.assertEqual(
            file.get_xml_content("xml/u14045.xml", "source", "file"),
            "/home/c/data/image/u14045.qcow2")

    def test_get_file_md5(self):
        self.assertEqual(file.get_file_md5("/home/c/data/image/u14045.qcow2"),
                         "0ce0f6fbf4e282ce63389cb8b37e7da4")


if __name__ == "__main__":
    unittest.main()
