"""
Example of writing parsed info into db
"""
import sys

import logging
from collections import defaultdict

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
    :return: dict[tuple(domain, ip), tuple(counter, set(url))]
    """
    grouped = defaultdict(lambda: (0, set()))

    for url, host_info in lst:
        t = grouped[host_info.domain, host_info.ip]
        t[1].add(url)
        grouped[host_info.domain, host_info.ip] = (t[0]+1, t[1])
    return grouped

def insert_grouped(groupped, urls_ids):
    """
    Function that inserts grouped items into db
    :param groupped: dict[tuple(domain, ip), tuple(counter, url)]
    :param urls_ids: dict[url, id]
    """

    for domain_ip, counter_url in groupped.items():
        counter, urls = counter_url
        domain, ip = domain_ip

        url_ids = [urls_ids[c] for c in urls]
        db_api.insert(domain=domain, ip=ip,
                      counter=counter_url[0],
                      urls_ids=url_ids)

def main():
    """
    First we insert urls into db, so we know their ids
    before starting parsing
    After that we group output by BATCH_SIZE
    :return:
    """
    urls = sys.argv[1:]
    urls = set(urls)

    connection = connector.get_connection(settings)

    urls_ids = db_api.insert_urls(connection, urls)  # type: dict

    for lst in split_every(BATCH_SIZE, data_from_urls(urls)):
        """
        Process in packs of BATCH_SIZE
        We group items by their (domain, ip)
        """
        logging.info('Saving %s into db', lst)
        groupped = group(lst)

        insert_grouped(groupped, urls_ids)

if __name__ == '__main__':
    main()
