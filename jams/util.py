#!/usr/bin/env python
# -*- encoding: utf-8 -*-
r"""Utility functions

Data I/O
========
.. autosummary::
    :toctree: generated/

    read_lab
    load_textlist
    expand_filepaths
    smkdirs
    filebase
    find_with_extension


JObject helpers
===============
.. autosummary::
    :toctree: generated/

    match_query
    query_pop


JamsFrame helpers
=================
.. autosummary::
    :toctree: generated/

    timedelta_to_float
    serialize_obj
"""

import os
import glob
import pandas as pd
import numpy as np
import re
import six


def timedelta_to_float(t):
    '''Convert a timedelta64[ns] to floating point (seconds)'''

    return t.astype(np.float) * 1e-9


def serialize_obj(obj):
    '''Custom serialization functionality for working with advanced data types.

    - Timedelta objects are convered to floats (in seconds)
    - numpy arrays are converted to lists
    - lists are recursively serialized element-wise

    '''
    if isinstance(obj, pd.tslib.Timedelta):
        return obj.total_seconds()

    elif isinstance(obj, np.ndarray):
        return obj.tolist()

    elif isinstance(obj, list):
        return [serialize_obj(x) for x in obj]

    return obj


def read_lab(filename, num_columns, delimiter=None, comment='#', header=False):
    """Read the rows of a labfile into memory.

    An effort is made to infer datatypes, and therefore numerical values will
    be mapped to ints / floats accordingly.

    Note: Any row with fewer than `num_columns` values will be back-filled
    with empty strings.

    Parameters
    ----------
    filename : str
        Path to a labfile.
    num_columns : int
        Number of columns in lab file.
    delimiter : str
        lab file delimiter
    comment : str
        lab file comment character
    header : bool
        if true, the first line will be skipped

    Returns
    -------
    columns : list of lists
        Columns of data in the labfile.
    """
    data = [list() for _ in range(num_columns)]
    first_row = True
    with open(filename, 'r') as input_file:
        for row_idx, line in enumerate(input_file, 1):
            if line.strip() == '':
                continue
            if line.startswith(comment):
                continue
            values = line.strip().split(delimiter, num_columns - 1)
            while len(values) < num_columns:
                values.append('')
            if header and first_row:
                first_row = False
                continue
            for idx, value in enumerate(values):
                try:
                    if "." in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass
                data[idx].append(value)

    return data


def load_textlist(filename):
    """Return a list of lines in a text file."""
    with open(filename, 'r') as fp:
        return [line.strip("\n") for line in fp]


def expand_filepaths(base_dir, rel_paths):
    """Expand a list of relative paths to a give base directory."""
    return [os.path.join(base_dir, os.path.normpath(rp)) for rp in rel_paths]


def smkdirs(dpath):
    """Safely make a directory path if it doesn't exist."""
    if not os.path.exists(dpath):
        os.makedirs(dpath)


def filebase(filepath):
    """Return the extension-less basename of a file path."""
    return os.path.splitext(os.path.basename(filepath))[0]


def find_with_extension(in_dir, ext, depth=3, sort=True):
    """Naive depth-search into a directory for files with a given extension.

    Parameters
    ----------
    in_dir : str
        Path to search.
    ext : str
        File extension to match.
    depth : int
        Depth of directories to search.
    sort : bool
        Sort the list alphabetically

    Returns
    -------
    matched : list
        Collection of matching file paths.
    """
    assert depth >= 1
    ext = ext.strip(os.extsep)
    match = list()
    for n in range(1, depth+1):
        wildcard = os.path.sep.join(["*"]*n)
        search_path = os.path.join(in_dir, os.extsep.join([wildcard, ext]))
        match += glob.glob(search_path)

    if sort:
        match.sort()
    return match


def match_query(string, query):
    '''Test if a string matches a functional query.

    Parameters
    ----------
    string : str
        The string to test

    query : string or callable
        Either a regular expression or a callable function

    Returns
    -------
    match : bool
        `True` if `query` is a callable and `query(string) == True`
        or if `query` is a regexp and `re.match(query, regexp)`

        `False` otherwise
    '''

    if six.callable(query):
        return query(string)

    elif isinstance(query, six.string_types):
        return (re.match(query, string) is not None)

    else:
        raise TypeError('Invalid query type: {:s}'.format(type(query)))

    return False


def query_pop(query, prefix, sep='.'):
    '''Pop a prefix from a query string.


    Parameters
    ----------
    query : str
        The query string

    prefix : str
        The prefix string to pop, if it exists

    sep : str
        The string to separate fields

    Returns
    -------
    popped : str
        `query` with a `prefix` removed from the front (if found)
        or `query` if the prefix was not found

    Examples
    --------
    >>> query_pop('Annotation.namespace', 'Annotation')
    'namespace'
    >>> query_pop('namespace', 'Annotation')
    'namespace'

    '''

    terms = query.split(sep)

    if terms[0] == prefix:
        terms = terms[1:]

    return sep.join(terms)
