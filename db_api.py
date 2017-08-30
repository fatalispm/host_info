import logging
from pymysql import OperationalError

from connector import get_connection

INSERT_URL = """
    INSERT INTO urls (url) VALUES (%s)
"""

INSERT_LINK = """
INSERT INTO domain_ip (domain, ip, counter) VALUES (%s, INET_ATON(%s), %s)
  ON DUPLICATE KEY UPDATE counter = counter + VALUES(counter);
"""

INSERT_URL_DOMAIN = """
INSERT IGNORE INTO url_domain (domain_id, url_id) VALUES (
  %s, %s
);"""

def insert_domain_url(cursor, url_id, domain_id):
    """
    :Parameters:
         - `cursor`: pymysql.cursor
         - `url_id`: str
         - `domain_id`: str
    """
    domains = [domain_id] * len(url_id)
    logging.info('Inserting url_id domain_id', url_id, domain_id)
    cursor.executemany(INSERT_URL_DOMAIN, zip(domains, url_id))

def insert(domain, ip, counter, urls_ids, connect=None):
    """
    :Parameters:
        - `connect`: pymysql.Connect
        - `domain`: str
        - `ip` : str
        - `urls_ids`: list of str
    """
    if not connect:
        connect = get_connection()

    try:
        with connect.cursor() as cursor:
            insert_domain_ip(cursor, domain, ip, counter)
            row_id = cursor.lastrowid
            insert_domain_url(cursor, urls_ids, row_id)

    except OperationalError:
        logging.exception('Failed to get a cursor')

    connect.commit()


def insert_domain_ip(cursor, domain, ip, counter):
    """
    :Parameters:
        - `c`: pymysql.cursor
        - `domain`: str
        - `link`: str
    """
    logging.info('Inserting ip and domain: %s %s %s', ip, domain, counter )
    cursor.execute(INSERT_LINK, (domain, ip, counter))


def insert_urls(connection, urls):
    """
    :Parameters:
        - `connection`: pymysql.Connection
        - `urls`: list of str
    :Return:
        dict[url, row_id]
    """
    logging.info('Inserting url %s', urls)

    url_ids = {}

    with connection.cursor() as cursor:
        for url in urls:
            cursor.execute(INSERT_URL, (url,))
            url_ids[url] = cursor.lastrowid

    connection.commit()

    return url_ids
