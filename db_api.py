"""
Module that provides basic API for inserting/updating info in db
"""

import logging
import time
import datetime

from pymysql import OperationalError, InternalError

from connector import get_connection


class DBAPIException(Exception):
    """
    Exception used for db api errors
    """


class DBAPI(object):
    """
    Class that encapsulates working with MySQL DB
    """

    INSERT_URL = """INSERT INTO urls (url, creation_time) VALUES (%s, %s)"""

    INSERT_LINK = """INSERT INTO domain_ip (domain, ip, url_id, counter)
    VALUES (%s, INET_ATON( % s), %s, %s)
    ON DUPLICATE KEY UPDATE counter = counter + VALUES (counter);
    """

    FETCH_URL_IDS = """SELECT
      id,
      url
    FROM urls
    WHERE creation_time = % s AND url IN % s;"""

    REMOVE_OLD_URLS = """DELETE FROM urls WHERE creation_time > %s;"""

    def __init__(self, user, password, host, database):
        self.user = user
        self.password = password
        self.host = host
        self.db = database

    @property
    def connection(self):
        if not getattr(self, '_connection', None):
            try:
                self._connection = get_connection(dict(
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    database=self.db
                ))
            except OperationalError as err:
                raise DBAPIException(err)
        return self._connection

    def delete_old_urls(self, hours=24):
        """
        Function that deletes old urls
        :Parameters:
            - `hours`: int
        """
        now = datetime.datetime.now()
        old_date = now - datetime.timedelta(hours=hours)
        prepared_old_date = old_date.strftime('%Y-%m-%d %H:%M:%S')

        with self.connection.cursor() as cursor:
            cursor.execute(self.REMOVE_OLD_URLS, (prepared_old_date,))
            self.connection.commit()

    def insert(self, data):
        """
        :Parameters:
            - `data`: list of tuple(domain, ip, url_id, counter)
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(self.INSERT_LINK, data)
                self.connection.commit()

        except InternalError as err:
            logging.exception('Wrong query when inserting %s', data)

    def get_url_ids(self, urls, timestamp):
        """
        Function that returns dict[url, id] for list of urls
        :Parameters:
             - `urls`: list of str
             - `timestamp`: str
        :Return:
             dict[url, id]
        """
        d = {}

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(self.FETCH_URL_IDS, (timestamp, urls))

                for id, url in cursor.fetchall():
                    d[url] = id
                self.connection.commit()
        except InternalError:
            logging.exception('Failed to execute query')
            raise

        except Exception:
            logging.exception('Unknown error occured')
            raise

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
            cursor.execute(self.INSERT_LINK, (domain,
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
            cursor.executemany(self.INSERT_URL, urls_date)

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
