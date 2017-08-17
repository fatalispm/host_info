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
    def find_all(self, element):
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

    def find_all(self, element):
        """
        :Paremeters:
            - `element`: str tag to find
        :Return:
            list of elements
        """
        return self.soup.find_all(element)

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
