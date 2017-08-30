"""
Basic unitility functions for everyday usage
"""

from itertools import islice


def split_every(n, iterable):
    """
    :Parameters:
         - `n` : int
         - `iterable`: iterable:
    :Return:
        generator that yields list of splitted chunks
    """
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield piece
        piece = list(islice(i, n))
