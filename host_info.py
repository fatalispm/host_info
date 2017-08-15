"""
Module for representing host info
"""
from __future__ import print_function
import datetime
import argparse

import psutil


def processes_count():
    """
    Return number of pcs
    :return: int
    """
    return len(psutil.pids())


def ram_usage():
    """
    Return ram usage
    :return int
    """
    mem = psutil.virtual_memory()
    return mem.available


def cpu_usage():
    """
    Return cpu usage
    :return int
    """
    return psutil.cpu_percent()


class InfoView(object):
    """
    Class used for presenting information about host
    """

    def __init__(self, **kwargs):
        """
        We pass arguments for correct showing of info
        m - stands for memory
        c - for cpu
        p - for processes
        a - all
        BTW, what should we do if all params are False?
        If all are False, we return everything
        :param kwargs: dict
        """
        self.mem = kwargs.pop('m', False)
        self.cpu = kwargs.pop('c', False)
        self.process_count = kwargs.pop('p', False)
        self.all = kwargs.pop('a', False)

        if not any([self.mem, self.cpu, self.process_count]):
            self.all = True

        if self.all:
            self.mem, self.cpu, self.process_count = [True] * 3
        super(InfoView, self).__init__()

    @property
    def ram_repr(self):
        """
        Returns memory usage
        :return str
        """

        return 'Memory usage: {ram_usage} '.format(ram_usage=ram_usage())

    @property
    def cpu_repr(self):
        """
        Returns cpu usage
        :return str
        """
        return 'Current cpu usage: {cpu_usage} '.format(cpu_usage=cpu_usage())

    @property
    def pc_repr(self):
        """
        Returns process count representation
        :return str
        """
        return 'Proc count: {processes_count} '.format(
            processes_count=processes_count())

    @property
    def _initial(self):
        """
        Formats an initial string, that returns current data
        :return str
        """
        return 'Date: {now} '.format(now=datetime.datetime.now())

    def show(self):
        """
        Method that returns a representation of the host info
        :return str
        """
        initial = self._initial
        if self.cpu:
            initial += self.cpu_repr
        if self.mem:
            initial += self.ram_repr
        if self.process_count:
            initial += self.pc_repr
        return initial


class FilePrinter(object):
    """
    A simple wrapper for appending info to file
    """

    def __init__(self, path):
        """
       :param path: str Path to file
       """
        self.path = path

    def __call__(self, _str):
        """
        :param _str: str string to write into the file
        """
        with open(self.path, 'a+') as f:
            f.write(_str + '\n')


def create_parser(description=''):
    """
    Function that creates parser
    :param description: str
    :return: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-p', help='Show number of processes',
                        action='store_true')
    parser.add_argument('-c', help='Show cpu usage',
                        action='store_true')
    parser.add_argument('-m', help='Memory usage',
                        action='store_true')
    parser.add_argument('-a', help='Show all info', action='store_true')
    parser.add_argument('--file', help='File path', type=str)
    return parser


def get_printer(args):
    """
    Function that returns printer
    :param args: argparse.args
    :return: Callable
    """
    printer = FilePrinter(args.file) if args.file else print
    return printer


def main():
    """
    The main function of the program
    :return:
    """
    parser = create_parser('Host information.')
    args = parser.parse_args()

    printer = get_printer(args)

    info = InfoView(**args.__dict__)
    printer(info.show())


if __name__ == '__main__':
    main()
