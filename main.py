"""
Example of writing parsed info into db
"""
import sys

import logging
from collections import defaultdict, Counter

import connector
import db_api
from parsing import data_from_urls
from utils import split_every
from local import settings

BATCH_SIZE = 10


def group(lst):
    """
    Function that groups lst by (domain, ip) and counter number
    of occurencs of all (domain, ip)
    :param lst: list of tuple(url, HostInfo)
    :return: dict[tuple(domain, ip, url), int]
    """
    return Counter((host_info.domain, host_info.ip, url) for url, host_info in
                   lst)


def prepare(groupped, url_ids):
    """

    :Parameters:
         - `groupped`: dict[tuple(domain, ip, url), int]
         - `url_ids`: dict[url, url_id]
    :return: list of tuple(domain, ip, url, counter)
    """

    for (domain, ip, url), counter in groupped.items():
        yield domain, ip, url_ids[url], counter


def main():
    """
    First we insert urls into db, so we know their ids
    before starting parsing
    After that we group output by BATCH_SIZE
    :return:
    """
    urls = sys.argv[1:]
    fetch_urls(urls)


def fetch_urls(urls):
    """
    Fetches urls and inserts them into db
    :param urls: list of str
    """
    urls = set(urls)
    db = db_api.DBAPI(settings)
    timestamp = db.insert_urls(urls)  # type: str
    url_ids = db.get_url_ids(urls, timestamp)
    for lst in split_every(BATCH_SIZE, data_from_urls(urls)):
        """
        Process in packs of BATCH_SIZE
        We group items by their (domain, ip)
        """
        logging.info('Saving %s into db', lst)
        groupped = group(lst)

        prepared_data = list(prepare(groupped, url_ids))
        db.insert(prepared_data)


if __name__ == '__main__':
    main()
