import logging

import time

import datetime
from pymysql import OperationalError, InternalError

from connector import get_connection

INSERT_URL = """
    INSERT INTO urls (url, creation_time) VALUES (%s, %s)
"""

INSERT_LINK = """
INSERT INTO domain_ip (domain, ip, url_id, counter) VALUES (%s, INET_ATON(%s), %s, %s)
  ON DUPLICATE KEY UPDATE counter = counter + VALUES(counter);
"""

FETCH_URL_IDS = """
    SELECT id, url FROM urls WHERE creation_time=%s AND url IN %s
;"""

REMOVE_OLD_URLS = """
DELETE FROM urls WHERE creation_time > %s;
"""


class DBAPIException(Exception):
    """
    Exception used for db api errors
    """


class DBAPI(object):
    """
    Class that encapsulates working with MySQL DB
    """

    def __init__(self, settings):
        self.settings = settings

    @property
    def connection(self):
        if not getattr(self, '_connection', None):
            try:
                self._connection = get_connection(self.settings)
            except OperationalError as err:
                raise DBAPIException(err)
        return self._connection


    def delete_old_urls(self, hours=24):
        """
        Function that deletes old urls
        :param hours: int
        """
        now = datetime.datetime.now()
        old_date = now - datetime.timedelta(hours=hours)
        prepared_old_date = old_date.strftime('%Y-%m-%d %H:%M:%S')

        with self.connection.cursor() as cursor:
            cursor.execute(REMOVE_OLD_URLS, (prepared_old_date,))

    def insert(self, data):
        """
        :Parameters:
            - `data`: list of tuple(domain, ip, url_id, counter)
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(INSERT_LINK, data)
        except OperationalError:
            logging.exception('Failed to get a cursor')

        except InternalError as err:
            logging.exception('Wrong query when inserting %s', data)

        self.connection.commit()

    def get_url_ids(self, urls, timestamp):
        """
        Function that returns dict[url, id] for list of urls
        :param urls: list of str
        :param timestamp: str
        :return: dict[url, id]
        """
        with self.connection.cursor() as cursor:
            cursor.execute(FETCH_URL_IDS, (timestamp, urls))
        d = {}

        for id, url in cursor.fetchall():
            d[url] = id
        self.connection.commit()
        return d

    def insert_domain_ip(self, domain, ip, counter, url_id):
        """
        :Parameters:
            - `c`: pymysql.cursor
            - `domain`: str
            - `link`: str
        """
        logging.info('Inserting ip and domain: %s %s %s', ip, domain, counter)
        with self.connection.cursor() as cursor:
            cursor.execute(INSERT_LINK, (domain,
                                         ip,
                                         counter,
                                         url_id))

    def insert_urls(self, urls):
        """
        :Parameters:
            - `urls`: list of str
            - `date`:
        :Return:
        """
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime(
            '%Y-%m-%d %H:%M:%S')
        logging.info('Inserting url %s', urls)
        urls_date = zip(urls, [timestamp] * len(urls))

        with self.connection.cursor() as cursor:
            cursor.executemany(INSERT_URL, urls_date)

        self.connection.commit()

        return timestamp

def get_db_api(settings):
    """
    Function that returns encapsulated db object
    Currently returns only one possible
    :param settings: dict
    :return: DBAPI
    """

    return DBAPI(settings)