"""
Module for connecting to mysql
"""

import pymysql

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
    if not settings:
        settings = local.settings

    return pymysql.connect(**settings)


def insert(connect, url, link, domain, ip):
    """
    :Parameters:
        - `connect`: pymysql.Connect
        - `url`: str
    """

    with connect.cursor() as c:
        insert_url(c, url)
        insert_ip(c, ip)
        insert_link(c, domain, link)
        insert_links_ips(c, ip, link, url)

    connect.commit()


def insert_links_ips(c, ip, link, url):
    """
    Insert ip, link, url connection into the db
    :Parameters:
        - `c`: pymysql.cursor
        - `url`: str
        - `ip`: str
        - `link`: str
    """
    c.execute(LINK_IPS, (link, ip, url))


def insert_link(c, domain, link):
    """
    :Parameters:
        - `c`: pymysql.cursor
        - `domain`: str
        - `link`: str
    """
    c.execute(INSERT_LINK, (link, domain))


def insert_ip(c, ip):
    """
    :Parameters:
        - `c`: pymysql.cursor
        - `ip`: str
    """
    c.execute(INSERT_IP_INFO, ip)


def insert_url(c, url):
    """
    :Parameters:
        - `c`: pymysql.cursor
        - `url`: str
    """
    c.execute(INSERT_URL, url)
