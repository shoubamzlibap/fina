#!/usr/bin/python
"""
Do basic sorting of transactions.

Author: Isaac Hailperin <isaac.hailperin@gmail.com>
"""

import sys

###
# Settings
###

OUTFILE = 'overview.csv'


###
# Globals
###

transactions = {}

# From all input files,
# * create montly sums per recepient and sender
# * create montly sumps per recepient and sender category (to be defined in special input file)

for infile in sys.arvg.pop():
    with open(infile, 'r') as infile_handle:
        reader = csv.DictReader(infile_handle)
        for row in reader:
            # do something with row.
