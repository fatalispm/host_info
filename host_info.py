"""
Module for representing host info
"""

import argparse
import datetime
import logging

import psutil

MEMORY_USAGE = 'Memory usage: %s '
CPU_USAGE = 'CPU usage: %s '
PROC_COUNT = 'Proc count: %s '
INITIAL = 'Date: %s '


class HostInfo(object):
    """
    Class responsible for providing information about system info
    """

    @staticmethod
    def processes_count():
        """
        :Return:
            int number of pcs
        """
        return len(psutil.pids())

    @staticmethod
    def ram_usage():
        """
        :Return:
            int ram usage
        """
        mem = psutil.virtual_memory()
        return mem.available

    @staticmethod
    def cpu_usage():
        """
        :Return:
            float cpu_usage
        """
        return psutil.cpu_percent()


def prepare_string(template, val):
    """
    :Parameters:
        - `template`: str template to use
        - `val`: str value to insert into the template

    :Return:
        str prepared string
     """
    return template % (val,)


def show(cpu=False, mem=False, process_count=False):
    """
    :Parameters:
        - `cpu`: bool show cpu
        - `mem`: bool show memory
        - `process_count`: bool show process_count

    :Return:
        str
     """
    initial = prepare_string(INITIAL, datetime.datetime.now())
    strings = [initial]

    if cpu:
        strings.append(prepare_string(CPU_USAGE, HostInfo.cpu_usage()))

    if mem:
        strings.append(prepare_string(MEMORY_USAGE, HostInfo.ram_usage()))

    if process_count:
        strings.append(prepare_string(PROC_COUNT, HostInfo.processes_count()))

    return '\n'.join(strings)


def print_to_file(path, show_string):
    """
    :Parameters:
       - `path`: str|list path to file
       - `show_string`: str string to write to file

    """
    if isinstance(show_string, list):
        show_string = '\n'.join(show_string)

    try:
        with open(path, 'a+') as f:
            f.write(show_string+'\n')
    except EnvironmentError as e:
        logging.error('Error while working with file %s', e)


def create_parser(description=''):
    """
    Function that creates parser
    :Parameters:
        - `description`: str name of the parser

    :Return:
        argparse.ArgumentParser
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


def validate_input(args):
    """
    Validates input from args
    :Parameters:
        - `args`: argparse.args

    :Return:
        bool
    """
    return any([args.mem, args.cpu, args.process])


def main():
    """
    The main function of the program
    """
    parser = create_parser('Host information.')
    args = parser.parse_args()

    if not validate_input(args):
        logging.error('Provide at least one parameter p/c/m')
        exit(0)

    response = show(cpu=args.cpu, mem=args.mem, process_count=args.process)

    if args.file:
        print_to_file(args.file, response)

    if args.console:
        print(response)


if __name__ == '__main__':
    main()
