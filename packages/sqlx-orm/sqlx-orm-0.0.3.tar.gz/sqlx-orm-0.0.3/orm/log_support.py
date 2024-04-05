from sqlexec.log_support import logger


def orm_insert_log(function, class_name, **kwargs):
    logger.debug("Exec func 'sqlbatis.orm.Model.%s' \n\t Class: '%s', kwargs: %s" % (function, class_name, kwargs))


def orm_delete_by_id_log(function, class_name, _id, update_by):
    logger.debug("Exec func 'sqlbatis.orm.Model.%s' \n\t Class: '%s', id: %d, update_by: %s" % (function, class_name, _id, update_by))


def orm_by_log(function, class_name, where, *args, **kwargs):
    logger.debug("Exec func 'sqlbatis.orm.Model.%s' \n\t Class: '%s', where: %s, args: %s, kwargs: %s" % (function, class_name, where, args, kwargs))


def orm_inst_log(function, class_name):
    logger.debug("Exec func 'sqlbatis.orm.Model.%s', Class: '%s'" % (function, class_name))


def orm_logical_delete_by_ids_log(function, class_name, ids, update_by, batch_size):
    logger.debug("Exec func 'sqlbatis.orm.Model.%s' \n\t Class: '%s', ids: %s, update_by: %s, batch_size: %s" % (
        function, class_name, ids, update_by, batch_size))


def orm_count_log(function, class_name, **kwargs):
    logger.debug("Exec func 'sqlbatis.orm.Model.%s' \n\t Class: '%s', kwargs: %s" % (function, class_name, kwargs))


def orm_find_log(function, class_name, *fields, **kwargs):
    logger.debug("Exec func 'sqlbatis.orm.Model.%s' \n\t Class: '%s', fields: %s, kwargs: %s" % (function, class_name, fields, kwargs))


def orm_find_by_id_log(function, class_name, _id, *fields):
    logger.debug("Exec func 'sqlbatis.orm.Model.%s' \n\t Class: '%s', id: %d, fields: %s" % (function, class_name, _id, fields))


def orm_find_by_ids_log(function, class_name, ids, *fields):
    logger.debug("Exec func 'sqlbatis.orm.Model.%s' \n\t Class: '%s', ids: %s, fields: %s" % (function, class_name, ids, fields))


def orm_page_log(function, page_num, page_size, class_name, *fields, **kwargs):
    logger.debug("Exec func 'pgsqlx.orm.Model.%s', page_num: %d, page_size: %d \n\t Class: '%s', fields: %s, kwargs: %s" % (
        function, page_num, page_size, class_name, fields, kwargs))


def orm_by_page_log(function, page_num, page_size, class_name, where, *args, **kwargs):
    logger.debug("Exec func 'sqlx-batis.orm.Model.%s', page_num: %d, page_size: %d \n\t Class: '%s', where: %s, args: %s, kwargs: %s" % (
        function, page_num, page_size, class_name, where, args, kwargs))
