"""
Module for retrieving ips/domains from url
"""

import time
import logging
import socket
import sys

from functools import wraps
from urlparse import urlparse

import requests

from parsers import parser_factory

LOGGING = False
DELAY = 1
RETRY = 3


class Page(object):

    """
    Class that represents html Page
    Provides methods like fetch_urls
    """

    def __init__(self, soap):
        """

        :Parameters:
            - `soap`: Parser
        """
        self.soap = soap

    def _find_links(self):
        """
        Method that returns all a tags on the page
        :Return:
            list of bs4.Element
        """
        return self.soap.find_all('a')

    def fetch_urls(self):
        """
        Method that returns list of urls
        :Return:
            generator
        """
        for a in self._find_links():
            yield a.get('href')


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
            logging.info('Calling request page with params %s', (args,))
            counter = 0
            while counter < tries:
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as err:
                    message = "Error: %s occured when parsing url: %s %s"
                    logging.error(message, err, args, kwargs)

                time.sleep(delay)
                counter += 1
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
    domain = _get_domain_from_url(url)
    ip = _get_ip_from_url(domain)
    return url, domain, ip


def _get_ip_from_url(domain):
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


def _get_domain_from_url(url):
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

    if domain.startswith('www.'):
        domain = domain[4:]

    return domain


@retry(DELAY, RETRY)
def request_page(url):
    """
    :Parameters:
        - `url`: str url of the page to request

    :Return:
        request.Response object
    """
    logging.info('Requesting url %s', url)
    return requests.get(url, timeout=3)


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

    response = (request_page(url) for url in urls)
    return (r.content for r in response if r)


def get_pages_from_contents(contents, parser):
    """
    Function that returns wrapped Page objects from contents of the pages
    :Parameters:
        - `urls`: list of str
        - `parse`: parser user can pass custom parser
    :Return:
        list of Page
    """
    for content in contents:
        yield Page(parser(content))


def list_of_links_from_contents(contents, parser=''):
    """
    Core function of the program, returns list of links from urls
    :Parameters:
        - `urls`: list of str
        - `parser`: str name of the parser to use
    :return generator
    """
    parser = parser_factory(parser)
    pages = get_pages_from_contents(contents, parser)
    for page in pages:
        for url in page.fetch_urls():
            yield url


def main():
    """
    Main function of the program
    """
    urls = sys.argv[1:]
    contents = request_pages(urls)

    for url in list_of_links_from_contents(contents):
        result = get_url_host_ip(url)
        if result:
            print result


if __name__ == '__main__':
    main()
