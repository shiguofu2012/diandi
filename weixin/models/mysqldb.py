# coding=utf-8
# !/usr/bin/python
'''
This is wrapper for MySQLdb;
mysql add/delete/update/find;
MysqlConfig  ---  config class for mysql;

Mysql        ---  mysql operation;
'''

import MySQLdb
from weixin.settings import LOG_MODEL as LOGGER


class MysqlConfig(object):
    '''
    mysql config class;

    host     ---  the mysql host ip or name;
    port     ---  the mysql port;
    user     ---  the username of the mysql;
    passwd   ---  the password of the mysql;
    db_name  ---  the database name;
    connect_timeout  --- timeout of connectiong error;
    autocommit       --- autocommit the execute sql statements;
    '''
    user = 'root'
    passwd = ''
    host = 'localhost'
    port = 3306
    db_name = ''
    connect_timeout = 10
    autocommit = False

    def __init__(self, *args, **kwargs):
        '''
        init mysql config parameters;
        '''
        # TODO check the params is legall;
        params_order = (
                "user", "passwd", "host", "port", "db_name",
                "connect_timeout", "autocommit")
        for index, value in enumerate(args):
            setattr(self, params_order[index], value)
        for param in params_order:
            value = kwargs.pop(param, '')
            if value:
                setattr(self, param, value)

    def set_user(self, user):
        '''
        set user name for mysql config;
        '''
        self.user = user

    def get_user(self):
        '''
        get the user of mysql config;
        '''
        return self.user

    def set_passwd(self, passwd):
        '''
        set the password for mysql config;
        '''
        self.passwd = passwd

    def get_passwd(self):
        '''
        get password for mysql config;
        '''
        return self.passwd

    def set_host(self, host):
        '''
        set host for mysql config;
        '''
        self.host = host

    def set_port(self, port):
        '''
        set the port for mysql config;
        '''
        self.port = port

    def get_port(self):
        '''
        get the port for mysql config;
        '''
        return self.port

    def set_dbname(self, dbname):
        '''
        set db name;
        '''
        self.db_name = dbname

    def get_dbname(self):
        '''
        get db name;
        '''
        return self.db_name

    def set_con_timeout(self, timeout):
        '''
        set the connect timeout for mysql;
        '''
        self.connect_timeout = timeout

    def get_con_timeout(self):
        '''
        get the connect timeout
        '''
        return self.connect_timeout

    def __str__(self):
        msg = ''
        msg += '*' * 30
        msg += '\nhost:\t %s\nport:\t %s\n' % (self.host, self.port)
        msg += "username: %s\tpassword: %s\n" % (self.user, self.passwd)
        msg += "dbname: %s\n" % self.db_name
        msg += "connect timeout: %s\n" % self.connect_timeout
        msg += "*" * 30
        return msg


class Mysql(object):
    '''
    mysql operation;
    '''
    def __init__(self, my_config):
        '''
        init params for mysql;
        config is instance of MysqlConfig
        '''
        self.con = None
        self.sql_config = my_config
        # self.user = my_config.user
        # self.passwd = my_config.passwd
        # self.dbname = my_config.db_name
        # self.host = my_config.host
        # self.port = my_config.port
        # self.timeout = my_config.connect_timeout
        self.get_con()

    def get_con(self):
        '''
        get connection and cursor of mysql db;
        '''
        self.con = MySQLdb.connect(
            host=self.sql_config.host, port=self.sql_config.port,
            user=self.sql_config.user, passwd=self.sql_config.passwd,
            db=self.sql_config.db_name,
            connect_timeout=self.sql_config.connect_timeout)
        self.con.set_character_set('utf8')
        self.cur = self.con.cursor(MySQLdb.cursors.DictCursor)

    def disconnect(self):
        '''
        disconnect from mysql;
        '''
        if self.con:
            self.cur.close()
            self.con.close()
            self.con = None

    def execute(self, sql_str, update=False):
        '''
        execute sql statements;
        '''
        try:
            ret = self.cur.execute(sql_str)
            if update:
                self.con.commit()
            return ret
        except Exception:
            self.disconnect()
            self.get_con()
            ret = self.cur.execute(sql_str)
            if update:
                self.con.commit()
            return ret

    def executemany(self, sql_str, data, update=False):
        '''
        executemany function;
        '''
        try:
            ret = self.cur.executemany(sql_str, data)
            if update:
                self.con.commit()
            return ret
        except Exception:
            ret = self.cur.executemany(sql_str, data)
            if update:
                self.con.commit()
            return ret

    def insert_batch(self, table, datas, update=True):
        '''
        save data batch;
        '''
        fields = ''
        values_list = []
        if not datas or not isinstance(datas, list):
            return False, "data is null or data format error"
        keys = datas[0].keys()
        for data in datas:
            if not fields:
                fields = self.list2fields(keys)
            tmp = []
            for field in keys:
                tmp.append(data.get(field))
            values_list.append(tmp)
        values = ''
        for i in range(len(keys)):
            if values:
                values = '%s, %s' % (values, '%s')
            else:
                values = '%s'
        sql = 'insert into %s(%s) values(%s)' % (table, fields, values)
        LOGGER.info("insert_batch:%s", sql)
        ret = self.executemany(sql, values_list, update)
        return ret, "OK"

    def dict2cond(self, cond, data=0):
        '''
        instance dict convert to sqlstatments;
        '''
        where = ''
        for key, value in cond.items():
            tmp = ''
            if isinstance(value, (int, long)):
                tmp = '`%s`=%d' % (key, value)
            elif isinstance(value, list):
                list_tmp = self.list2values(value)
                if list_tmp:
                    tmp = '`%s` in (%s)' % (key, list_tmp)
            elif isinstance(value, dict):
                tmp = ''
                for operat, data_v in value.items():
                    if operat == '$nin':
                        tmp_dict = '`%s` not in (%s)' % (key, self.list2values(data_v))
                    elif isinstance(data_v, (int, long)):
                        tmp_dict = '`%s`%s%d' % (key, operat, data_v)
                    else:
                        tmp_dict = "`%s`%s'%s'" % (key, operat, data_v)
                    if not tmp:
                        tmp = tmp_dict
                    else:
                        tmp = '%s and %s' % (tmp, tmp_dict)
            else:
                tmp = "`%s`='%s'" % (key, value)
            if where and not data:
                where = '%s and %s' % (where, tmp)
            elif where:
                where = '%s, %s' % (where, tmp)
            else:
                where = tmp
        return where

    def dict2search(self, search_condition):
        """
        search_condition:
            {field: ['1234', 'dfd']}
        """
        search_sql = ''
        search_op = search_condition.pop("search_op", 'and')
        for search_fields, search_data in search_condition.items():
            if isinstance(search_data, basestring):
                tmp = '`%s` like \'%%%s%%\'' % (search_fields, search_data)
            elif isinstance(search_data, list):
                tmp = '`%s` like ' % search_fields
                for index, search_value in enumerate(search_data):
                    if len(search_data) - 1 == index:
                        tmp += '\'%%%s%%\'' % search_value
                    else:
                        tmp += '\'%%%s%%\' or ' % search_value
            search_sql += tmp + search_op + ' '
        rindex = search_sql.rfind('and')
        if rindex != -1:
            search_sql = search_sql[0: rindex]
        rindex = search_sql.rfind("or")
        if rindex != -1:
            search_sql = search_sql[0: rindex]
        return search_sql

    def list2values(self, values):
        '''
        instance list convert to sql IN statement;
        '''
        value_str = ''
        for value in values:
            if value_str:
                if isinstance(value, int):
                    value_str = '%s, %d' % (value_str, value)
                else:
                    value_str = '%s, "%s"' % (value_str, value)
            else:
                if isinstance(value, int):
                    value_str = '%d' % (value)
                else:
                    value_str = "'%s'" % value
        return value_str

    def list2fields(self, fields):
        field_str = ''
        for field in fields:
            if field_str:
                field_str = '%s, `%s`' % (field_str, field)
            else:
                if field == '*':
                    field_str = '%s' % field
                else:
                    field_str = '`%s`' % field
        return field_str

    def increase(self, table, condition, field='times', count=1):
        where = self.dict2cond(condition)
        sql_str = 'update `%s` set `%s`=`%s`+%s where %s'\
            % (table, field, field, count, where)
        LOGGER.info(sql_str)
        ret = self.execute(sql_str, True)
        if not ret:
            return False
        return True

    def count(self, table, cond={}):
        where = self.dict2cond(cond)
        if where:
            sql_str = 'select count(id) from {} where {}'.format(table, where)
        else:
            sql_str = 'select count(id) from {}'.format(table)
        ret = self.execute(sql_str)
        if not ret:
            return 0
        result = self.cur.fetchone()
        return result['count(id)']

    def search_poetry(self, keyword, page=1, count=20, fields=None):
        skip = (page - 1) * count
        if skip < 0:
            skip = 0
        if not fields:
            fields = 'id,title,content,author,dynasty,likes,banner'
        else:
            fields = ",".join(fields)
        sql_str = u"select {} from "\
            u"poetry where match(title,content,author) against(\"{}\") "\
            u"limit {},{}".\
            format(fields, keyword, skip, count)
        sql_str = sql_str.encode("utf-8")
        ret = self.execute(sql_str)
        LOGGER.info("sql: %s, ret: %s", sql_str, ret)
        if not ret:
            return []
        return self.cur.fetchall()

    def search_poetry_widget(
            self, keyword, page=1, count=20, fields=None, sort=None):
        skip = (page - 1) * count
        if skip < 0:
            skip = 0
        if not fields:
            fields = 'id,title,content,author,dynasty,likes,banner'
        else:
            fields = ",".join(fields)
        if sort:
            sql_str = u"select {} from "\
                u"poetry where match(title,content,author) against(\"{}\") "\
                u"order by likes desc limit {},{}".\
                format(fields, keyword, skip, count)
        else:
            sql_str = u"select {} from "\
                u"poetry where match(title,content,author) against(\"{}\") "\
                u"limit {},{}".\
                format(fields, keyword, skip, count)
        sql_str = sql_str.encode("utf-8")
        ret = self.execute(sql_str)
        LOGGER.info("sql: %s, ret: %s", sql_str, ret)
        if not ret:
            return []
        return self.cur.fetchall()

    def get(self, table, cond={}, page=1, count=20, fields=['*'], sort={}):
        field_str = self.list2fields(fields)
        where = self.dict2cond(cond)
        if where:
            sql_str = 'select %s from `%s` where %s'\
                            % (field_str, table, where)
        else:
            sql_str = 'select %s from `%s`' % (field_str, table)
        if sort:
            sort_sql = ''
            sort_key = sort.keys()[0]
            reverse = sort.values()[0]
            if reverse >= 1:
                sort_sql = 'order by %s ASC' % sort_key
            else:
                sort_sql = 'order by %s DESC' % sort_key
            sql_str = '%s %s' % (sql_str, sort_sql)
        skip = (page - 1) * count
        sql_str += ' limit %s, %s' % (skip, count)
        LOGGER.info(sql_str)
        ret = self.execute(sql_str, True)
        if not ret:
            return []
        return self.cur.fetchall()

    def match_data(self, table, condition, fields, page, count):
        if not fields:
            fields = ['*']
        field_str = self.list2fields(fields)
        where = self.dict2search(condition)
        sql_str = 'select %s from `%s` where %s order by likes desc '\
            'limit %s, %s' % (
                    field_str, table, where, (page - 1) * count, count)
        LOGGER.info(sql_str)
        ret = self.execute(sql_str)
        if not ret:
            return []
        return self.cur.fetchall()

    def get_one(self, table, cond={}, fields=['*'], sort={}):
        self.disconnect()
        self.get_con()
        field_str = self.list2fields(fields)
        where = self.dict2cond(cond)
        if where:
            sql_str = 'select %s from `%s` where %s'\
                            % (field_str, table, where)
        else:
            sql_str = 'select %s from `%s`' % (field_str, table)
        LOGGER.info("get_one: %s", sql_str)
        if sort:
            sort_sql = ''
            sort_key = sort.keys()[0]
            reverse = sort.values()[0]
            if reverse >= 1:
                sort_sql = 'order by %s ASC limit 1' % sort_key
            else:
                sort_sql = 'order by %s DESC limit 1' % sort_key
            sql_str = '%s %s' % (sql_str, sort_sql)
        ret = self.execute(sql_str, True)
        if not ret:
            self.disconnect()
            return {}
        return self.cur.fetchone()

    def random_get(self, table, fields=['*'], page=1, count=20):
        field_str = self.list2fields(fields)
        skip = (page - 1) * count
        sql_str = 'select %s from `%s` order by likes desc limit %s,%s' % (
                field_str, table, skip, count)
        ret = self.execute(sql_str)
        if not ret:
            return []
        return self.cur.fetchall()

    def update(self, table, cond, data, update=True):
        where = self.dict2cond(cond)
        set_data = self.dict2cond(cond=data, data=1)
        if where:
            sql_str = 'update `%s` set %s where %s' % (table, set_data, where)
        else:
            sql_str = 'update `%s` set %s' % (table, set_data)
        LOGGER.info("update: %s" % sql_str)
        ret = self.execute(sql_str, update)
        if not ret:
            return False
        return ret

    def delete(self, table, cond):
        where = self.dict2cond(cond)
        if where:
            sql_str = 'delete from `{}` where {}'.format(table, where)
        else:
            return False
        LOGGER.info("delete: %s", sql_str)
        ret = self.execute(sql_str, True)
        if not ret:
            return False
        return ret

    def insert(self, table, data, update=True):
        SQL_FORMAT = "insert into `%s` (%s) values (%s)"
        keys = data.keys()
        values = data.values()
        field_str = self.list2fields(keys)
        value_str = self.list2values(values)
        sql_str = SQL_FORMAT % (table, field_str, value_str)
        LOGGER.info("insert: %s" % sql_str)
        try:
            ret = self.execute(sql_str, update)
            if not ret:
                return False, "unknow Error"
            if update:
                self.con.commit()
            return ret, "OK"
        except Exception as e:
            LOGGER.error("ex: %s", e, exc_info=True)
            return False, e

    def group_by(self, table, condition, group_by_fields, fields, page, count):
        where = self.dict2cond(condition)
        select_fields = ','.join(fields)
        group_fields = self.list2fields(group_by_fields)
        skip = (page - 1) * count
        if condition:
            sql_str = 'select {select_fields} from {table} where {condition} '\
                'group by {group_fields} limit {start},{count}'.format(
                            select_fields=select_fields,
                            table=table,
                            condition=where,
                            group_fields=group_fields,
                            start=skip,
                            count=count)
        else:
            sql_str = 'select {select_fields} from {table} '\
                'group by {group_fields} limit {start},{count}'.format(
                            select_fields=select_fields,
                            table=table,
                            group_fields=group_fields,
                            start=skip,
                            count=count)
        LOGGER.info(sql_str)
        try:
            ret = self.execute(sql_str)
            if not ret:
                return []
            return self.cur.fetchall()
        except Exception as e:
            LOGGER.error("ex: %s", e, exc_info=True)
            return []

    def return_error(self):
        self.con.rollback()
        self.disconnect()

    def increaseMutex(
            self, table, cond, field, count=1, greater=0, check=0, data={}):
        self.disconnect()
        self.get_con()
        where = self.dict2cond(cond)
        if where:
            sql_str = "select * from %s where %s for update" % (table, where)
        else:
            sql_str = "select * from %s for update" % table
        LOGGER.info('increaseMutex: %s' % sql_str)
        try:
            ret = self.execute(sql_str)
            if not ret:
                self.return_error()
                return False, 'unknow Error execute:%s!' % sql_str
            record = self.cur.fetchone()
            if not record:
                # self.con.rollback()
                self.return_error()
                return False, 'Not Found Record %s' % where
            original = record.get(field)
            try:
                original = long(original)
            except Exception as e:
                self.return_errro()
                return False, '%s type is not int' % field
            comp = original + count
            if check and comp < greater:
                self.return_error()
                return False, '%d is less than %d' % (original, -count)
            if data:
                data.update({field: comp})
            else:
                data = {field: comp}
            ret = self.update(table, cond, data, False)
            if not ret:
                self.return_error()
                return False, 'unknow Error execute:%s' % 'update'
            self.con.commit()
            self.disconnect()
            return True, record
        except Exception as e:
            # self.con.rollback()
            self.disconnect()
            return False, e

    def updateMutexCheck(self, table, cond, data, status, fields=['*']):
        '''
        update the record with data according to the original value
        of status with mutex.

        parameters:

        table <---> table name.
        cond  <---> query condition.
        data  <---> update data.
        status<---> check the status, if not match, then did not update.
        '''
        self.disconnect()
        self.get_con()
        SQL_STR = "select %s from `%s` where %s for update"
        where = self.dict2cond(cond)
        fields_str = self.list2fields(data.keys())
        # values_str = self.list2values(data.values())
        sql_str = SQL_STR % (fields_str, table, where)
        LOGGER.info("updateMutexCheck: %s" % sql_str)
        result = False
        msg = ''
        try:
            ret = self.execute(sql_str)
            record = self.cur.fetchone()
            if not record:
                self.con.rollback()
                result = False
                msg = "Not Found Record By %s" % where
            else:
                flag = 1
                for check_key, check_value in status.items():
                    value = record.get(check_key)
                    if isinstance(check_value, (int, str, unicode)):
                        if value != check_value:
                            flag = 0
                            break
                    elif isinstance(check_value, list):
                        if value not in check_value:
                            flag = 0
                    elif isinstance(check_value, dict):
                        for op, c_value in check_value.items():
                            express = "%s %s %s" % (value, op, c_value)
                            if not eval(express):
                                flag = 0
                                break
                    else:
                        flag = 0
                    if not flag:
                        break
                if flag == 0:
                    self.con.rollback()
                    result = False
                    msg = "status check did not match"
                else:
                    ret = self.update(table, cond, data)
                    self.con.commit()
                    result = ret
                    msg = "OK"
        except Exception as ex:
            self.con.rollback()
            result = False
            msg = ex
        finally:
            self.disconnect()
        return result, msg

    def transaction(self, **kwargs):
        self.disconnect()
        self.get_con()
        result = True
        msg = ''
        try:
            for table, data in kwargs.items():
                if isinstance(data, list):
                    successed, msg = self.insert_batch(
                        table, data, update=False)
                    if not successed:
                        result = False
                        msg = 'insert into %s error: %s' % (table, msg)
                        break
                    else:
                        msg += 'save to %s, %d records' % (table, successed)
                else:
                    successed, msg = self.insert(table, data, update=False)
                    if not successed:
                        result = False
                        msg = 'insert into %s error: %s' % (table, msg)
                        break
                    else:
                        msg += 'save to %s, %d records' % (table, successed)
            if result:
                LOGGER.info('commit')
                self.con.commit()
            else:
                self.con.rollback()
        except Exception as e:
            self.con.rollback()
            result = False
            msg = "Exception happened: %s" % e
        finally:
            self.disconnect()
        return result, msg

    def increaseMultiMutex(
            self, table, cond, field, count=1,
            greater=0, check=0, data={}, uniqKey=""):
        self.disconnect()
        self.get_con()
        where = self.dict2cond(cond)
        if not where or not uniqKey:
            return False, "cond is null or uniqKey is null"
        sql_str = "select * from %s where %s for update" % (table, where)
        LOGGER.info('increaseMultiMutex: %s' % sql_str)
        try:
            ret = self.execute(sql_str)
            if not ret:
                self.return_error()
                return False, 'unknow Error execute:%s!' % sql_str
            records = self.cur.fetchall()
            for record in records:
                original = record.get(field)
                try:
                    original = long(original)
                except ValueError:
                    self.return_error()
                    return False, '%s type is not int' % field
                comp = original + count
                if comp <= 0:
                    count = comp
                # if check and comp < greater:
                #     self.return_error()
                #     return False, '%d is less than %d' % (original, -count)
                update_count = 0 if comp < 0 else comp
                if data:
                    data.update({field: update_count})
                else:
                    data = {field: comp}
                uniq = record.get(uniqKey)
                update_cond = {uniqKey: uniq}
                ret = self.update(table, update_cond, data, False)
                if not ret:
                    self.return_error()
                    return False, 'unknow Error execute:%s' % 'update'
                if comp >= 0:
                    break
            self.con.commit()
            self.disconnect()
            return True, record
        except Exception as ex:
            # self.con.rollback()
            self.disconnect()
            return False, ex

    def update_mutex(self, table, cond, data, insert=True):
        '''
        lock the data befor update;
        if the data doesnot exists, insert it or not according to the insert;
        '''
        self.disconnect()
        self.get_con()
        where = self.dict2cond(cond)
        LOGGER.info(where)
        sql_stat = "select * from %s where %s for update" % (table, where)
        succ = False
        msg = ''
        try:
            ori_data = self.execute(sql_stat)
            LOGGER.info(ori_data)
            if not ori_data:
                msg = self.insert(table, data)
                succ = True
            else:
                msg = self.update(table, cond, data)
            self.con.commit()
            self.disconnect()
        except Exception as ex:
            msg = "ex: %s" % ex
        return succ, msg

    def commit(self):
        return self.con.commit()
