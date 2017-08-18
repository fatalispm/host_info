"""
Module that contains parsers
"""

from abc import ABCMeta, abstractmethod

from bs4 import BeautifulSoup 

class Parser(object):
    """
    Basic class for Parsers
    """

    ___metaclass__ = ABCMeta

    @abstractmethod 
    def __init__(self, content):
        """
        :Parameters:
            - `content`: str
        """
        pass

    @abstractmethod
    def find_all(self, *args, **kwargs):
        """
        Function that find all elements with given tag
       
        :Parameters:
            - `element`: str
        """
        pass

class BeautifulSoupParser(Parser):
    """
    Parser that uses bs4 lib
    """

    def __init__(self, content):
        """
        :Parameters:
            - `content`: str
        """
        self.soup = BeautifulSoup(content)

    def find_all(self, *args, **kwargs):
        """
        :Paremeters:
            - `args`: list of params
            - `kwargs`: dict of params
        :Return:
            list of elements
        """
        return self.soup.findAll(*args, **kwargs)

def parser_factory(parser):
    """
    :Parameters:
        - `parser`: str name of the parser to use
    :Return:
        Parser
    """
    return {
        'BeautifulSoup': BeautifulSoupParser
    }.get(parser) or BeautifulSoupParser
