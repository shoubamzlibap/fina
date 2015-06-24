#!/usr/bin/python
"""
Do basic sorting of transactions.

Author: Isaac Hailperin <isaac.hailperin@gmail.com>
"""

import sys
import csv
import hashlib
from collections import defaultdict
import calendar

###
# Settings
###

OUTFILE = 'overview.csv'


###
# Globals
###

transaction_ids = []

#transactions = defaultdict(defaultdict(float))
transactions = defaultdict( lambda : defaultdict(float))

# From all input files,
# * create montly sums per recepient and sender
# * create montly sumps per recepient and sender category (to be defined in special input file)

csv.register_dialect('semicolon', delimiter=';')

for infile in sys.argv[1:]:
    with open(infile, 'r') as infile_handle:
        reader = csv.DictReader(infile_handle, dialect='semicolon')
        for row in reader:
            # Calculate uniqe transaction id, so that overlapping input files do not
            # corrupt the result.
            transaction_id = hashlib.sha256(''.join(row.values())).hexdigest()
            if not transaction_id in transaction_ids:
                transaction_ids.append(transaction_id)
            else:
                continue
            considered_date = 'Valutadatum'
            year = '20' + row[considered_date][6:]
            month = calendar.month_name[int(row[considered_date][3:5])]
            transaction_key = row['Beguenstigter/Zahlungspflichtiger']
            if not transaction_key:
                transaction_key = row['Buchungstext']
            transactions[month + ' ' + year][transaction_key] += \
                float(row['Betrag'].replace(',','.'))

#sys.exit()
for month,tr in transactions.items():
    print
    print month
    print '==========================='
    for key,val in tr.items():
        print key + ' :: ' + str(val)
