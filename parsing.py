#!usr/bin/python2.7
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

DELAY = 1
RETRY = 3

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
    return url, domain, ip


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
        return ''

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

def list_of_links_from_contents(contents, parser=''):
    """
    Core function of the program, returns list of links from urls
    :Parameters:
        - `urls`: list of str
        - `parser`: str name of the parser to use
    :return generator
    """
    parser = parser_factory(parser)
    for content in contents:
        parsed_page = parser(content)
        for item in parsed_page.find_all(href=True):
            url = item.get('href')
            logging.info('Processed url %s', url)
            if url:
                yield url

def main():
    """
    Main function of the program
    """
    urls = sys.argv[1:]
    contents = request_pages(urls)

    for url in list_of_links_from_contents(contents):
        logging.info('Retrieving url %s', url)
        result = get_url_host_ip(url)
        if result:
            print result


if __name__ == '__main__':
    main()
