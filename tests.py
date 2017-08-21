"""
Module for testing functionality of the parsing module
"""

import unittest 

from collections import defaultdict
from socket import error

from parsing import (get_url_host_ip, domain_from_url, get_ip_from_url,
                     RETRY, request_page, RetryException, 
                     list_of_links_from_contents)
from parsers import BeautifulSoupParser

def fake_ip(ip): 
    if ip:
        return '1.1.1.1'
    raise error()

def get(page, calls=defaultdict(int), **kwargs):
    """
    for all other pages keep track of them called
    if called 3 times return True
    """
    retries = {
        'valid_url': 1,
        'retry_url': RETRY,
        'broken_url': RETRY+1
    }
    calls[page] += 1
    if calls[page] == retries[page]:
        return True
    raise Exception()
    
class TestUrlParsing(unittest.TestCase):
    
    """
    Test URL parsing
    """
    
    def setUp(self):
        import parsing
        self.original = parsing.socket.gethostbyname
        parsing.socket.gethostbyname = fake_ip
        
        
    def test_get_url_host_ip(self):
        valid_url = 'http://vk.com'
        
        url, host, ip = get_url_host_ip(valid_url)
        
        self.assertIsNotNone(url)
        self.assertIsNotNone(host)
        self.assertIsNotNone(ip)

        self.assertEqual(url, valid_url)
        self.assertEqual(host, 'vk.com')
        self.assertEqual(ip, '1.1.1.1')
        
    def test_get_url_host_ip_with_wrong_data(self):
        invalid_url = 'http:/ww.vk.com'
        
        url, host, ip = get_url_host_ip(invalid_url)
        
        self.assertEqual(url, invalid_url)
        self.assertEqual(host, '')
        self.assertEqual(ip, '')
        
        
    def test_get_domain_removes_www(self):
        valid_url = 'http://www.vk.com'
        
        domain = domain_from_url(valid_url)
        self.assertEqual(domain, 'vk.com')
    
    def test_get_domain_works_without_www(self):
        valid_url = 'http://vk.com'
        
        domain = domain_from_url(valid_url)
        self.assertEqual(domain, 'vk.com')
    
    def test_get_ip_from_domain(self):
        valid_domain = 'http://vk.com'
        result = get_ip_from_url(valid_domain)
        
        self.assertEqual(result, fake_ip(1))
        
    
    def tearDown(self):
        import parsing
        parsing.socket.gethostbyname = self.original


class TesBS4Parser(unittest.TestCase):
    
    """
    Test functionality of BS4 parser
    """
    
    def test_fetching_urls(self):
        page = """
              <a href="vk.com"></a>
              <a href="/"></a>
              <img href="facebook.com"></img>
              """
        parser = BeautifulSoupParser(page)
        
        result = parser.find_all(href=True)
        
        self.assertEqual(len(result), 3)
        
    def test_fetching_urls_from_wrong_page(self):
        page = """
               {"id": "1"}
               """
        parser = BeautifulSoupParser(page)
        
        result = parser.find_all(href=True)
        
        self.assertEqual(len(result), 0)
        
class TestRequestingPages(unittest.TestCase):
    def setUp(self):
        import parsing
        parsing.requests.get = get
        
    def test_request_page_ok(self):
        url = 'valid_url'
        result = request_page(url)
        
        self.assertTrue(result)
        
    def test_retry(self):
        url = 'retry_url'
        result = request_page(url)
        
        self.assertTrue(result)
        
    def test_throws_retry_exception(self):
        url = 'broken_url'
        with self.assertRaises(RetryException):
           request_page(url)
        
class TestFetchingLinks(unittest.TestCase):
    def setUp(self):
        self.pages = ["""
              <a href="vk.com"></a>
              <a href="/"></a>
              <img href="facebook.com"></img>
              """, '<a></a>', '<a href="youtube.com"></a>']
    
    def test_fetching_links(self):
        result = list(list_of_links_from_contents(self.pages))
        self.assertEqual(len(result), 4)
    
    

    

