from base64 import b64decode

import pymysql
from common.constants.database_config import HOST_DICT, PASSWD_DICT
from common.util.encrypt_util import decrypt_aes


def get_connection_by_schema(key, schema, env='test'):
    passwd = decrypt_aes(key, b64decode(PASSWD_DICT[env])).decode()
    return pymysql.connect(host=HOST_DICT[env], port=4000, user="root", passwd=passwd,
                           db=schema, charset="utf8")


def get_mpi_connection(key, env='test'):
    """
    获取ncpcs_mpi库的连接
    :return: 数据库连接
    """
    passwd = decrypt_aes(key, b64decode(PASSWD_DICT[env])).decode()
    return pymysql.connect(host=HOST_DICT[env], port=4000, user="root", passwd=passwd,
                           db="ncpcs_mpi", charset="utf8")


def get_sibling_connection(key, env='test'):
    """
    获取ncpcs_sibling库的连接
    :return: 数据库连接
    """
    passwd = decrypt_aes(key, b64decode(PASSWD_DICT[env])).decode()
    return pymysql.connect(host=HOST_DICT[env], port=4000, user="root", passwd=passwd,
                           db="ncpcs_sibling", charset="utf8")


def get_medical_data_analyze_connection(key, env='test'):
    """
    获取ncpcs_medical_data_analyze库的连接
    :return: 数据库连接
    """
    passwd = decrypt_aes(key, b64decode(PASSWD_DICT[env])).decode()
    return pymysql.connect(host=HOST_DICT[env], port=4000, user="root", passwd=passwd,
                           db="ncpcs_medical_data_analyze", charset="utf8")


def get_tumour_stage_connection(key, env='test'):
    """
    获取ncpcs_solid_tumour_stage库的连接
    :return: 数据库连接
    """
    passwd = decrypt_aes(key, b64decode(PASSWD_DICT[env])).decode()
    return pymysql.connect(host=HOST_DICT[env], port=4000, user="root", passwd=passwd,
                           db="ncpcs_tumour_stage", charset="utf8")


def get_tumor_connection(key, env='test'):
    """
    获取ncpcs_tumour库的连接
    :return: 数据库连接
    """
    passwd = decrypt_aes(key, b64decode(PASSWD_DICT[env])).decode()
    return pymysql.connect(host=HOST_DICT[env], port=4000, user="root", passwd=passwd,
                           db="ncpcs_tumor", charset="utf8")