import re
from functools import lru_cache
from .log_support import page_log
from .constant import DYNAMIC_REGEX, CACHE_SIZE

# Don't remove. Import for not repetitive implementation
from sqlexec.sql_support import get_batch_args, get_named_sql_args, is_mapping, get_mapping_sql_args, require_limit, try_mapping, get_table_select_sql


def simple_sql(sql: str, *args, **kwargs):
    return get_named_sql_args(sql, **kwargs) if kwargs else (sql, args)


def get_page_start(page_num: int, page_size: int):
    assert page_num >= 1 and page_size >= 1, "'page_name' and 'page_size' should be higher or equal to 1"
    return (page_num - 1) * page_size


@lru_cache(maxsize=2*CACHE_SIZE)
def is_dynamic_sql(sql: str):
    return re.search(DYNAMIC_REGEX, sql)


@lru_cache(maxsize=2*CACHE_SIZE)
def _get_sql_type(sql: str):
    """
    :return: 0: placeholder, 1: dynamic, 2: named mapping
    """
    if is_dynamic_sql(sql):
        return 1
    if is_mapping(sql):
        return 2
    return 0

