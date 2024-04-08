"""Taxref common module"""

from collections import namedtuple

PdReadCts = namedtuple('PdReadCts', ['sep', 'header', 'index_col', 'dtype', 'na_filter'])

# default reader constants for most of Taxref versions
pdReadCts = PdReadCts(sep='\t',
                      header=0,
                      index_col='CD_NOM',
                      dtype={
                          'CD_NOM': 'string'
                      },
                      na_filter=False)
