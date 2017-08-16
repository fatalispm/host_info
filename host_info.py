"""
Module for representing host info
"""
import argparse
import datetime

import psutil
import logging



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

    def __init__(self, mem, cpu, process_count, show_all):
        """

        :param mem: bool
        :param cpu: bool
        :param process_count: bool
        :param show_all: bool
        """
        self.mem = mem
        self.cpu = cpu
        self.process_count = process_count

        show_all = show_all or not \
            any([self.mem, self.cpu, self.process_count])

        if show_all:
            self.mem, self.cpu, self.process_count = [True] * 3

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

    def __init__(self, path=None, console=False):
        """
       :param path: str Path to file
       :param console: bool display result into console?
       """
        self.path = path
        self.console = console

    def print_to_file(self, show_string):
        """

        :param show_string: str
        :return:
        """
        try:
            with open(self.path, 'a+') as f:
                f.writelines([show_string])
        except EnvironmentError as e:
            logging.error('Error while working with file {e}'.format(e=e))

    def print_to_console(self, show_string):
        """

        :param show_string: str
        :return:
        """
        print show_string

    def __call__(self, show_string):
        """
        :param show_string: str string to write into the file
        """
        if self.console:
            self.print_to_console(show_string)

        if self.path:
            self.print_to_file(show_string)



def create_parser(description=''):
    """
    Function that creates parser
    :param description: str
    :return: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-p', help='Show number of processes',
                        action='store_true', dest='process')
    parser.add_argument('-c', help='Show cpu usage',
                        action='store_true', dest='cpu')
    parser.add_argument('-m', help='Memory usage',
                        action='store_true', dest='mem')
    parser.add_argument('-a', help='Show all info', action='store_true',
                        dest='all')
    parser.add_argument('--console', help='Include console', default=True,
                        dest='console')
    parser.add_argument('--file', help='File path', type=str)
    return parser


def get_printer(args):
    """
    Function that returns printer
    :param args: argparse.args
    :return: Callable
    """
    return FilePrinter(args.file, args.console)


def main():
    """
    The main function of the program
    :return:
    """
    parser = create_parser('Host information.')
    args = parser.parse_args()

    printer = get_printer(args)

    info = InfoView(cpu=args.cpu, mem=args.mem, show_all=args.all,
                    process_count=args.process)
    printer(info.show())


if __name__ == '__main__':
    main()
