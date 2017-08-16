"""
Module for retrieving ips/domains from url
"""

import logging
import socket
import sys
from urlparse import urlparse

import grequests
from bs4 import BeautifulSoup

LOGGING = False


class Page(object):

    """
    Class that represents html Page
    Provides methods like fetch_urls
    """

    def __init__(self, soap):
        """

        :param soap: BeautifulSoup
        """
        self.soap = soap

    @staticmethod
    def _get_domain_from_url(url):
        """
        Fetches domain from url
        :param url: str
        :return: str
        """
        splitted_url = urlparse(url)
        domain = splitted_url.netloc

        if domain.startswith('www.'):
            domain = domain[5:]

        return domain

    @staticmethod
    def _fetch_url_from_a(a):
        """

        :param a: bs4.element
        :return:  str string parsed from a element
        """
        return a.get('href')

    def fetch_urls(self):
        """
        Method that returns list of urls
        :return: generator
        """
        for a in self.soap.find_all('a'):
            yield self._fetch_url_from_a(a)

    @staticmethod
    def _get_ip_from_url(domain):
        """

        :param domain: str domain of the webpage
        :return: str ip address
        """
        try:
            return socket.gethostbyname(domain)
        except socket.gaierror:
            if LOGGING:
                logging.error("Can't fetch ip from domain %s", domain)

    def get_urls_hosts_ips(self):
        """
        Returns triple (url, domain, ip) only if every part is present
        :return generator
        """
        for url in self.fetch_urls():

            domain = self._get_domain_from_url(url)
            ip = self._get_ip_from_url(url)

            if domain and ip:
                yield (url, domain, ip)


def parse(content):
    """
    Parses page and returns a wrapper around html page
    :param content: str
    :return: Page
    """
    return Page(BeautifulSoup(content))


def error_handler(request, exception):
    """
    Handler for handling exceptions when retrieving pages
    :param request: grequests.request
    :param exception: Exception
    :return:
    """
    if LOGGING:
        logging.error(exception)


def request_pages(urls):
    """

    :param urls: list of str
    :return: generator of str that contains page body
    """
    rs = (grequests.get(u, timeout=3) for u in urls)
    response = grequests.imap(rs, exception_handler=error_handler)
    return (r.content for r in response if r is not None)


def main():
    """
    Main function of the program
    """
    urls = sys.argv[1:]

    for content in request_pages(urls):
        page = parse(content)
        for result in page.get_urls_hosts_ips():
            print result


if __name__ == '__main__':
    main()
