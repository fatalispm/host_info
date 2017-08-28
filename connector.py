"""
Module for connecting to mysql
"""
import logging
import pymysql
from mysqlx import OperationalError

import local

INSERT_URL = """
INSERT INTO urls (url) VALUES (%s)
  ON DUPLICATE KEY UPDATE urls.modification_time = NOW();
  """

INSERT_LINK = """
INSERT INTO link_info (link, domain) VALUES (%s, %s)
  ON DUPLICATE KEY UPDATE link_info.counter = link_info.counter + 1;
"""

INSERT_IP_INFO = """INSERT INTO ip_info (ip) VALUES (%s)
  ON DUPLICATE KEY UPDATE ip_info.counter = ip_info.ip + 1;
  """

LINK_IPS = """
INSERT INTO link_ips(link_id, ip_id, url_id) VALUES (
  (SELECT id FROM link_info WHERE link = %s),
  (SELECT id FROM ip_info WHERE ip = %s),
  (SELECT id FROM urls WHERE url = %s)
);"""


def get_connect(settings=None):
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


def insert(connect, url, link, domain, ip):
    """
    :Parameters:
        - `connect`: pymysql.Connect
        - `url`: str
    """

    try:
        with connect.cursor() as cursor:
            insert_url(cursor, url)
            insert_ip(cursor, ip)
            insert_link(cursor, domain, link)
            insert_links_ips(cursor, ip, link, url)
    except OperationalError:
        logging.exception('Failed to get a cursor')

    connect.commit()


def insert_links_ips(cursor, ip, link, url):
    """
    Insert ip, link, url connection into the db
    :Parameters:
        - `c`: pymysql.cursor
        - `url`: str
        - `ip`: str
        - `link`: str
    """
    logging.info('Inserting link_ips %s %s %s', ip, link, url)
    cursor.execute(LINK_IPS, (link, ip, url))


def insert_link(cursor, domain, link):
    """
    :Parameters:
        - `c`: pymysql.cursor
        - `domain`: str
        - `link`: str
    """
    logging.info('Inserting link and domain: %s %s', link, domain)
    cursor.execute(INSERT_LINK, (link, domain))


def insert_ip(cursor, ip):
    """
    :Parameters:
        - `c`: pymysql.cursor
        - `ip`: str
    """
    logging.info('Inserting ip %s', ip)
    cursor.execute(INSERT_IP_INFO, ip)


def insert_url(cursor, url):
    """
    :Parameters:
        - `c`: pymysql.cursor
        - `url`: str
    """
    logging.info('Inserting url %s', url)
    cursor.execute(INSERT_URL, url)
