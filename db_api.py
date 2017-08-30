import logging

import time

import datetime
from pymysql import OperationalError

from connector import get_connection

INSERT_URL = """
    INSERT INTO urls (url, creation_time) VALUES (%s, %s)
"""

INSERT_LINK = """
INSERT INTO domain_ip (domain, ip, url_id, counter) VALUES (%s, INET_ATON(%s), %s, %s)
  ON DUPLICATE KEY UPDATE counter = counter + VALUES(counter);
"""

FETCH_URL_IDS = """
    SELECT id, url FROM urls WHERE creation_time=%s AND url in %s
;"""

REMOVE_OLD_URLS = """
DELETE FROM urls WHERE creation_time > %s;
"""


def delete_old_urls(connection, hours=24):
    now = datetime.datetime.now()
    old_date = now - datetime.timedelta(hours=hours)
    prepared_old_date = old_date.strftime('%Y-%m-%d %H:%M:%S')

    with connection.cursor() as cursor:
        cursor.execute(REMOVE_OLD_URLS, (prepared_old_date,))


def insert(data, connect=None):
    """
    :Parameters:
        - `connect`: pymysql.Connect
        - `data`: list of tuple(domain, ip, url_id, counter)
    """
    if not connect:
        connect = get_connection()

    try:
        with connect.cursor() as cursor:
            cursor.executemany(INSERT_LINK, data)
    except OperationalError:
        logging.exception('Failed to get a cursor')

    connect.commit()


def get_url_ids(connection, urls, timestamp):
    """
    Function that returns dict[url, id] for list of urls
    :param connection: pymysql.Connection
    :param urls: list of str
    :param timestamp: str
    :return: dict[url, id]
    """
    with connection.cursor() as cursor:
        cursor.execute(FETCH_URL_IDS, (timestamp, urls))
    d = {}

    for id, url in cursor.fetchall():
        d[url] = id
    connection.commit()
    return d


def insert_domain_ip(cursor, domain, ip, counter, url_id):
    """
    :Parameters:
        - `c`: pymysql.cursor
        - `domain`: str
        - `link`: str
    """
    logging.info('Inserting ip and domain: %s %s %s', ip, domain, counter)
    cursor.execute(INSERT_LINK, (domain, ip, counter, url_id))


def insert_urls(connection, urls):
    """
    :Parameters:
        - `connection`: pymysql.Connection
        - `urls`: list of str
        - `date`:
    :Return:
    """
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    logging.info('Inserting url %s', urls)
    urls_date = zip(urls, [timestamp] * len(urls))

    with connection.cursor() as cursor:
        cursor.executemany(INSERT_URL, urls_date)

    connection.commit()

    return timestamp
