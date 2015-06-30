#!/usr/bin/python
"""
Do basic sorting of transactions.

Author: Isaac Hailperin <isaac.hailperin@gmail.com>
"""

import sys
import csv
import hashlib
from collections import defaultdict
from collections import OrderedDict
import calendar
import re

# TODO:
# add csv output

###
# Settings
###

OUTFILE = 'overview.csv'
DEFAULT_GROUP_FILE = 'samples/Umsatz_Gruppen.csv'

# From all input files,
# * create montly sums per recepient and sender
# * create montly sumps per recepient and sender category (to be defined in special input file)

def parse_input():
    """
    Parse all input files and return a dict with the data

    """
    csv.register_dialect('semicolon', delimiter=';')
    transaction_ids = []
    transactions = defaultdict( lambda : defaultdict(float))
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
                month = row[considered_date][3:5]
                transaction_key = row['Beguenstigter/Zahlungspflichtiger']
                if not transaction_key:
                    transaction_key = row['Buchungstext']
                transactions[year + ' ' + month][transaction_key] += \
                    float(row['Betrag'].replace(',','.'))
    return transactions


def print_transactions(transactions):
    """
    Print all transactions with some formatting.

    transactions: a dict of dicts, containing all transactions
    """
    for month,tr in transactions.items():
        print
        print month
        print '==========================='
        for key,val in tr.items():
            print key + ' :: ' + str(val)


def get_groups(group_file=DEFAULT_GROUP_FILE):
    """
    Get transactions groups, return a dict of regular expressions

    """
    transaction_groups = defaultdict(list)
    transaction_group_res = {}
    with open(group_file, 'r') as group_file_handle:
        reader = csv.DictReader(group_file_handle)
        for row in reader:
            for group_name,group_re in row.items():
                if group_re:
                    transaction_groups[group_name].append(group_re)
    check_uniquenes(transaction_groups)
    for group_name,group_res in transaction_groups.items():
        transaction_group_res[group_name] = '|'.join(group_res)
    return transaction_group_res


def check_uniquenes(transaction_groups):
    """
    Check for doubles in transaction_groups.

    transaction_groups: dict of transactions groups
    """
    group_members = [i for v in transaction_groups.values() for i in v]
    num_occurence = defaultdict(int)
    for member in group_members:
        num_occurence[member] += 1
    doubles = [k for k,v in num_occurence.items() if v > 1]
    if doubles:
        print 'The following items are not unique in group configuration:'
        print doubles
        exit()
    # now we also check for regex matches
    for member_re in group_members:
        for member in group_members:
            if member_re == member:
                continue
            if re.search(member_re, member, re.IGNORECASE):
                print member + ' is not a unique regular expression, it matches with ' + member_re
                exit()


def group_transactions(transactions):
    """
    Group transactions according to config sheet.

    transactions: all transactions in dict form

    """
    grouped_transactions = defaultdict( lambda : defaultdict(float))
    groups = get_groups()
    for month,m_transactions in transactions.items():
        for who in m_transactions.keys():
            for group_name,group_re in groups.items():
                if re.search(group_re, who, flags=re.IGNORECASE):
                    grouped_transactions[month][group_name] += m_transactions[who]
                    m_transactions.pop(who, None)
        # do something with the rest of m_transactions
        for who in m_transactions.keys():
            grouped_transactions[month]['NOT GROUPED ' + who] = m_transactions[who]
            m_transactions.pop(who, None)
    # sort transactions according to month
    sorted_transactions = OrderedDict()
    months = [m for m,t in grouped_transactions.items()]
    months.sort()
    for month in months:
        month_named = calendar.month_name[int(month.split()[1])] + ' ' + month.split()[0]
        sorted_transactions[month_named] = grouped_transactions[month]
    return sorted_transactions

transactions = parse_input()
grouped_transactions = group_transactions(transactions)
if __name__ == '__main__':
    print_transactions(grouped_transactions)

