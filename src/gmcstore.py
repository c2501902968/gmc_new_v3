#  !/usr/bin/env python3
#  -*- coding: UTF-8 -*-

import pymysql
import gmclog as log

logger = log.Loggings()


class Mysql():
    def __init__(self, address, port, user, passwd, char_set):
        '''
        description: 类的初始化 函数，数据库对象mysql在初始化时直接连接数据库，并获取cursor对象
        param {
            self：类对象
            address：要连接的数据库的ip地址
            port：要连接的数据库端口
            user：连接数据库用户名
            passwd：连接数据库密码
            char_set:连接用字符集，一搬为“utf-8”（默认）
        } 
        return: 
            None
        '''
        try:
            self.conn = pymysql.connect(address,
                                        user,
                                        passwd,
                                        charset=char_set,
                                        port=port)
            self.cur = self.conn.cursor()
            self.cur.execute("use image")
        except Exception as e:
            logger.error("connection database failed")
            logger.error(e)
            exit(-1)

    def __del__(self):  # 析构函数，实例删除时触发
        self.cur.close()
        self.conn.close()

    def query(self, sql):
        self.cur.execute(sql)
        return self.cur.fetchall()

    def exec1(self, sql):
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(str(e))

    def is_exist(self, object, value, table):
        '''
        description：判断 table 表中 object 中 value 值是否存在
        return：
            True：exist
            False：doesn't exist
        '''
        result = self.query(
            "SELECT * FROM %s WHERE %s = '%s' AND deleted = 0" %
            (table, object, value))
        return True if result else False

    def is_insert(self, name):
        '''
        description:判断是否可以添加虚拟机
        return:
            True：可以添加
            False：已经存在了
        '''
        result = self.query("SELECT deleted FROM instance WHERE name = '%s'" %
                            (name))
        return True if result else False

    def update_value(self, object1, value1, object2, value2, table):
        self.exec1("UPDATE %s SET %s='%s' WHERE %s = '%s' AND deleted = 0 " %
                   (table, object2, value2, object1, value1))

    def update_time(self, object1, value1, object2, table):
        '''更新数据库table表中object1中值为value1的object2的值为现在时间'''
        self.exec1("UPDATE %s SET %s=now() WHERE %s = '%s' AND deleted = 0" %
                   (table, object2, object1, value1))

    def get_value(self, object1, value, object2, table):
        '''从table数据库，查找object1为value对应的object2的值'''
        if object2 == 'deleted' or object2 == 'delete_at':
            result = self.query("SELECT %s FROM %s WHERE %s = '%s' " %
                                (object2, table, object1, value))
        else:
            result = self.query(
                "SELECT %s FROM %s WHERE %s = '%s' AND deleted = 0 " %
                (object2, table, object1, value))
        return result[0]

    def delete_value(self, object, value, table):
        '''删除虚拟机/镜像'''
        self.exec1("DELETE FROM %s WHERE %s ='%s' " % (table, object, value))

    def delete_value_all(self, table):
        '''删除所有的虚拟机/镜像，清空数据库'''
        self.exec1("DELETE FROM %s " % (table))

    def display(self, table):
        '''显示table的值'''
        results = self.query("SELECT * from %s" % table)
        return results

    def is_vm_exist(self, name):
        '''通过虚拟机的名字判断是否exist该虚拟机'''
        return True if self.is_exist("name", name, "instance") else False

    def insert_vm(self, name, uuid, mirror_location, mirror_hash):
        '''添加虚拟机'''
        self.exec1(
            "INSERT INTO instance(name,uuid,create_at, mirror_location, \
                mirror_hash) VALUES ('%s', '%s', now(),'%s', '%s')" %
            (name, uuid, mirror_location, mirror_hash))
        logger.debug("insert_vm {name}".format(name=name))

    def delete_vm(self, name):
        ''' 删除虚拟机'''
        self.delete_value("name", name, "instance")
        logger.debug("delete vm-{name}".format(name=name))

    def delete_vm_all(self):
        ''' 删除所有虚拟机 '''
        self.delete_value_all("instance")
        logger.debug("delete all vm")

    def update_vm_time(self, name, time):
        '''更新数据库instance表的时间'''
        self.update_time("name", name, time, "instance")
        logger.debug("update vm-{name} {time}".format(name=name, time=time))
        if time == "delete_at":
            self.update_value("name", name, "deleted", 1, "instance")
            logger.debug("update vm-{name} deleted".format(name=name))

    def update_vm_status(self, name, status):
        ''' update虚拟机的状态'''
        self.update_value("name", name, "vm_status", status, "instance")
        logger.debug("update vm-{name} vm_status {status} ".format(name=name, status=status))

    def update_vm_mirror_location(self, name, location):
        '''用于更新数据库imageLau表的位置'''
        self.update_value("name", name, "mirror_location", location,
                          "instance")
        logger.debug("update vm-{name} location".format(name=name))

    def update_vm_mirror_hash(self, name, hash):
        '''update镜像hash '''
        self.update_value("name", name, "mirror_hash", hash, "instance")
        logger.debug("update vm-{name} mirror's hash".format(name=name))

    def update_vm_trusted(self, name, trusted):
        '''update的可信度'''
        if trusted == 0:
            self.update_value("name", name, "trusted", "UnKnown", "instance")
        elif trusted == 1:
            self.update_value("name", name, "trusted", "UnTrusted", "instance")
        else:
            self.update_value("name", name, "trusted", "Trusted", "instance")
        logger.debug("update vm-{name} trusted ".format(name=name))

    def get_value_by_name(self, name, value):
        '''根据虚拟机的名字查找value'''
        result = self.get_value("name", name, value, "instance")
        logger.debug("vm-{name} {value}: {result} ".format(name=name,
                                                           value=value,
                                                           result=result))
        return result

    def display_vm(self):
        '''显示vm的信息'''
        result = self.display("instance")
        if not result:
            logger.error("Error: display_vm fail")
            return
        else:
            for ROW in result:
                id = ROW[0]
                name = ROW[1]
                uuid = ROW[2]
                create_at = ROW[3]
                update_at = ROW[4]
                delete_at = ROW[5]
                deleted = ROW[6]
                vm_status = ROW[7]
                mirror_location = ROW[8]
                mirror_hash = ROW[9]
                trusted = ROW[10]
                logger.debug(
                    "instance: id={id},name={name},uuid={uuid},create_at={create_at},\
                    update_at={update_at}, delete_at=delete_at,deleted=deleted,vm_status=vm_status,\
                    mirror_location=mirror_location,mirror_hash=mirror_hash,trusted=trusted"
                    .format(id=id,
                            name=name,
                            uuid=uuid,
                            create_at=create_at,
                            update_at=update_at,
                            delete_at=delete_at,
                            deleted=deleted,
                            vm_status=vm_status,
                            mirror_location=mirror_location,
                            mirror_hash=mirror_hash,
                            trusted=trusted))
                # print("id=%s,name=%s,uuid=%s,create_at=%s,update_at=%s,delete_at=%s,deleted=%d,image_ref=%s,vm_status=%s,trusted=%s" %  (id,name,uuid,create_at,update_at,delete_at,deleted,image_ref,vm_status,trusted))
