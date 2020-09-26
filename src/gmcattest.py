# !/usr/bin/env python3
# -*-encoding:utf-8-*-
'''
Description: GMC attestation module
Author: cj
Date: 2020-09-23 10:58:36
LastEditTime: 2020-09-25 22:01:58
LastEditors: cj
'''

import gmclog as glog
import gmcstore as gsql
import gmcfile as gfile1

logger = glog.Loggings()
db = gsql.Mysql("localhost", 3306, "root", "c", "utf8")
file = gfile1.File()


class Attest():
    def __init__(self, guest_name):
        self.guest_name = guest_name

    def check_image_hash(self):
        '''
        description: 通过判读镜像hash来判断镜像的可信性
        param : guest_name：要验证的虚拟机
        return: 0:unknown 1:untrusted 2:trusted
        '''
        mirror_location = db.get_value_by_name(self.guest_name,
                                               "mirror_location")[0]
        # logger.debug(
        #     "mirror_location: {location}".format(location=mirror_location))

        mirror_hash = db.get_value_by_name(self.guest_name, "mirror_hash")[0]
        # logger.debug("mirror_hash: {hash}".format(hash=mirror_hash))

        real_hash = file.get_file_md5(mirror_location)
        logger.debug("real_hash: {real_hash}".format(real_hash=real_hash))

        if (not mirror_location) or (not mirror_hash) or (not real_hash):
            logger.debug("{name} trusted：{trusted}".format(
                name=self.guest_name, trusted=0))
            return 0
        if mirror_hash == real_hash:
            logger.debug("{name}  trusted：{trusted}".format(
                name=self.guest_name, trusted=2))
            return 2
        else:
            logger.debug("{name}  trusted：{trusted}".format(
                name=self.guest_name, trusted=1))
            return 1

    def update_hash(self):
        '''
        description: 更新虚拟机的hash值
        return {type} 
        '''
        mirror_location = db.get_value_by_name(self.guest_name,
                                               "mirror_location")[0]
        logger.debug("update_hash: mirror_location: {location}".format(
            location=mirror_location))

        new_hash = file.get_file_md5(mirror_location)
        db.update_vm_mirror_hash(self.guest_name, new_hash)
        logger.debug("update_hash: {name} new_hash: {hash}".format(
            name=self.guest_name, hash=new_hash))


# if __name__ == "__main__":
#     att = Attest("u14045")
#     name = "u14045"
#     uuid = "9a1e3f7d-18cc-0e96-a88a-2b09284d06f7"
#     image_location = "/home/c/data/gmc_new_v2/test/xml/u14045.xml"
#     image_hash = "5c6f8b4f5a971116909f6751111ee1f5"

#     db.insert_vm(name, uuid, image_location, image_hash)
#     print(att.check_image_hash())
#     print(att.update_hash())
#     db.delete_vm("u14045")
