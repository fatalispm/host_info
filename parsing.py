"""
Module for retrieving ips/domains from url
"""

import time
import logging
import socket
import sys

from functools import wraps
from itertools import izip_longest
from urlparse import urlparse
from collections import namedtuple

import requests

from parsers import parser_factory
from patch import patch

DELAY = 1
RETRY = 3

HostingInfo = namedtuple('HostingInfo', ('link', 'ip', 'domain'))

class RetryException(Exception):
    """
    Exception to be used for retry decorator function
    """
    pass


def retry(delay, tries):
    """
    Decorator for retrying number of attempts with some delay
    :Parameters:
        - `delay`: int
        - `tries`: int
    :Return:
        wrapped function
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            logging.info('Calling %s %s', func.__name__, args)
            counter = 0
            while counter < tries:
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    message = 'Error ocurred when running %s %s %s'
                    logging.exception(message, func.__name__, args, kwargs)

                time.sleep(delay)
                counter += 1
            msg = 'Function %s failed after %s attempts'
            raise RetryException(msg % (func.__name__, tries))

        return inner

    return wrapper


def get_url_host_ip(url):
    """
    Function that returns triple (url, domain, ip)
    :Parameters:
       - `url`: str url
    :Return:
       generator triple (url, domain, ip) only if every part is present
    """
    domain = domain_from_url(url)
    ip = get_ip_from_url(domain)
    return HostingInfo(link=url, domain=domain, ip=ip)


def get_ip_from_url(domain):
    """
    :Parameters:
        - `domain`: str domain of the webpage
    :Return:
        str ip address
    """
    try:
        return socket.gethostbyname(domain)
    except socket.error:
        logging.error("Can't fetch ip from domain %s", domain)
        return '0.0.0.0'


def domain_from_url(url):
    """
    Fetches domain from url
    :Parameters:
        - `url`: str
    :Return:
        str
    """
    logging.info('Getting domain from %s', url)

    splitted_url = urlparse(url)
    domain = splitted_url.netloc

    return domain[4:] if domain.startswith('www.') else domain


@retry(DELAY, RETRY)
def request_page(url):
    """
    :Parameters:
        - `url`: str url of the page to request

    :Return:
        request.Response object
    """
    logging.info('Requesting url %s', url)
    return requests.get(url, timeout=3, verify=False)


def request_pages(urls):
    """
    Function that returns list of pages content from the list of urls
    Ignores exceptions

    :Parameters:
        - `urls`: list of str
    :Return:
        generator of str that contains page body
    """
    logging.info('Requesting pages %s', urls)
    for url in urls:
        try:
            page = request_page(url)
            yield page.content
        except RetryException as err:
            logging.exception('Failed to retrieve page: %s', url)
            print('Wrong url %s' % url)


def list_of_links_from_contents(contents, urls=None, parser=''):
    """
    Core function of the program, returns list of links from urls
    :Parameters:
        - `urls`: list of str
        - `parser`: str name of the parser to use
    :return generator
    """
    if not urls:
        urls = []

    parser = parser_factory(parser)
    for url, content in izip_longest(urls, contents):
        if not content:
            continue
        parsed_page = parser(content)
        for item in parsed_page.find_all(href=True):
            link = item.get('href')
            logging.info('Processed url %s', link)
            if link:
                yield url, link


def data_from_urls(urls):
    """
    :Parameters:
        - urls: list of str

    :Return:
        generator of (url, (link, domain, ip))
    """
    contents = request_pages(urls)

    for url, link in list_of_links_from_contents(contents, urls):
        logging.info('Retrieving url %s', link)
        result = get_url_host_ip(link)
        if result:
            yield url, result


def main():
    """
    Main function of the program
    """
    urls = sys.argv[1:]

    class Response(object):
        def __init__(self, str):
            self.content = str

    def wrapper(*args, **kwargs):
        return Response("""<a href="vk.co"></a>
        <a href="bb.com"></a>
        """)

    with patch('requests.get', wrapper):
        for url, data in data_from_urls(urls):
            print url, data

if __name__ == '__main__':
    main()
