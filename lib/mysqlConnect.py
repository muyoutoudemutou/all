# coding=utf-8
# !/usr/bin/env python3

import pymysql


# 创建链接,autocommit=False,   # 是否自动提交事务
config = {
    'host': 'localhost',
    'port': 3306,
    'user': '',
    'password': '',
    'db': '',
    'charset': 'utf8mb4',
    #'cursorclass': pymysql.cursors.Cursor,  # 选择 Cursor 类型
    'cursorclass': pymysql.cursors.DictCursor
}
#mysql工具类
class MySQLconnect():

    def __init__(self,user,password,db,port=3306,host='localhost'):
        self.config = {
                'host': host,
                'port': port,
                'user': user,
                'password': password,
                'db': db,
                'charset': 'utf8mb4',
                #'cursorclass': pymysql.cursors.Cursor,  # 选择 Cursor 类型
                'cursorclass': pymysql.cursors.DictCursor,
                'read_timeout':60,
                'write_timeout':60
            }
        self.db = pymysql.connect(**self.config)
        self.cursor = self.db.cursor()

    def execute(self, sql,args=None):
        try:
            # 获取游标
            if isinstance(args, list) and len(args) > 1:
                self.cursor.executemany(sql, args)
            elif isinstance(args, str):
                self.cursor.execute(sql, [args])
            elif isinstance(args, list) and len(args) == 1:
                self.cursor.execute(sql, args[0])
            elif args:
                self.cursor.execute(sql, args)
            else:
                self.cursor.execute(sql)
            self.db.ping(reconnect=True)
            self.db.commit()
            # cursor.fetchone()
            # cursor.fetchmany(3)

            return self.cursor.fetchall()
        except pymysql.err.OperationalError as e:  #因为连接超时，重新生成连接
            self.db.close()
            self.db = pymysql.connect(**self.config)
            self.cursor = self.db.cursor()
            # 获取游标
            if isinstance(args, list) and len(args) > 1:
                self.cursor.executemany(sql, args)
            elif isinstance(args, str):
                self.cursor.execute(sql, [args])
            elif isinstance(args, list) and len(args) == 1:
                self.cursor.execute(sql, args[0])
            elif args:
                self.cursor.execute(sql, args)
            else:
                self.cursor.execute(sql)
            self.db.ping(reconnect=True)
            self.db.commit()
            # cursor.fetchone()
            # cursor.fetchmany(3)

            return self.cursor.fetchall()

    def close(self):
        self.db.close()