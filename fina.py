#!/usr/bin/python
"""
Do basic sorting of transactions.

Author: Isaac Hailperin <isaac.hailperin@gmail.com>
"""

"""
usage: ./fina.py input files
"""

import sys
import csv
import hashlib
from collections import defaultdict
from collections import OrderedDict
import calendar
import re

from pprint import pprint

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
                try:
                    year = '20' + row[considered_date][6:]
                except KeyError:
                    continue
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

def print_transactions_as_csv(transactions):
    """
    Print all transactions as csv

    Structure:
    month1,group1,group2, ...,no_group1,nogroup2, ....
    month2,group1,group2, ...,no_group1,nogroup2, ....
    [{},{}]

    groups and no_groups should be a uniq list, built from all months, so that 
    it is easy to see how a certain group evolves over the month

    Also, groups should be sorted according to their overall sum, so that the
    largest sums are to the left.

    """
    restructured_transactions = restructure(transactions)
    sorted_sums = sort_by_value_and_groups(restructured_transactions)
    csv_data = combine(restructured_transactions, sorted_sums)
    field_names = ['Monat'] + [x[0] for x in sorted_sums]
    out_file = 'Ausgaben.csv'
    with open(out_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)
    print('Ergebnis wurd in die Datei ' + out_file + ' geschrieben.')

def combine(restructured_transactions, sorted_sums):
    """
    Combine restructured_transactions and sorted_sums in way suitable for writing 
    with a dict writer.

    """
    csv_data = []
    for month_tr in restructured_transactions:
        month = month_tr.keys()[0]
        transactions = month_tr.values()[0]
        transactions.update({'Monat': month})
        csv_data.append(transactions)
    sums = dict(sorted_sums)
    sums.update({'Monat':'Summe'})
    csv_data.append(sums)
    return csv_data

def sort_by_value_and_groups(transactions):
    """
    Sort according to grouped and ungroupped, within these sort by
    highest overall sum.
    
    transactions: output of restructure()

    """
    # calculate overall sums
    all_groups = transactions[0].values()[0]
    all_sums = defaultdict(float)
    for month_tr in transactions:
        for group,value in month_tr.values()[0].items():
            all_sums[group] += value
    # devide by grouped and ungrouped
    grouped = [ (k,v) for k,v in all_sums.items() if not k.startswith('NOT GROUPED')]
    ungrouped = [ (k,v) for k,v in all_sums.items() if k.startswith('NOT GROUPED')]
    # sort
    grouped.sort(key=lambda x: x[1])
    ungrouped.sort(key=lambda x: x[1])
    return grouped + ungrouped

def restructure(transactions):
    """
    Restructure transactions, so that each month every possible positin gets listed,
    even if its value is zero.

    transactions: ordered dict of transactions
    """
    all_months = [tr.items() for month,tr in transactions.items()]
    all_groups_listed = [[x[0] for x in g] for g in all_months]
    all_groups = set([item for sublist in all_groups_listed for item in sublist])
    all_transactions = []
    for month,tr in transactions.items():
        months_transactions = {month: {}}
        for group in all_groups:
            value = tr.get(group, 0)
            months_transactions[month][group] = value
        all_transactions.append(months_transactions)
    return all_transactions



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
    #print_transactions(grouped_transactions)
    print_transactions_as_csv(grouped_transactions)

