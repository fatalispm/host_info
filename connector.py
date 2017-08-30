"""
Module for connecting to mysql
"""
import logging
import pymysql
from mysqlx import OperationalError

import local


def get_connection(settings=None):
    """
    :Parameters:
        - `settings`: dict of settings
    :return:
        pymysql.Connect
    """
    logging.info('Getting connection with settings : %s', settings)
    if not settings:
        settings = local.settings

    try:
        return pymysql.connect(**settings)
    except OperationalError:
        logging.exception("Can't connect to the database with settings: %s",
                          settings)
