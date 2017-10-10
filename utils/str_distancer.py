#!/usr/bin/python3

import csv
import distance
import psycopg2

from pprint import pprint

street_range_filepath = '~/git/chicago_tickets/data/Chicago_Street_Names.csv'

def postgres_conn():
    connstr = "port=5433 dbname=tickets host=%s user=tickets password=tickets" % "localhost"
    conn = psycopg2.connect(connstr)

    return conn

def valid_streets(db):
    streets = []
    cursor = db.cursor()

    cursor.execute("SELECT DISTINCT(street) FROM street_ranges")
    [ streets.append(l[0].strip()) for l in cursor.fetchall() if l ]

    return streets

def ticket_streets(db):
    streets = []
    cursor = db.cursor()

    cursor.execute("SELECT DISTINCT(street_name) FROM ticket_addrs")
    [ streets.append(l[0].strip()) for l in cursor.fetchall() if l and l[0] ]

    return streets

#todo clean up.
def closest_leven(token, comparers, n=1):
    levens = [ (c, distance.nlevenshtein(token, c)) for c in comparers ]
    
    lowest_val = 1
    lowest_comparers = []
    for comparer, levens_dist in levens:
        if levens_dist < lowest_val:
            lowest_comparers = [(comparer, levens_dist)]
            lowest_val = levens_dist

        elif levens_dist == lowest_val:
            lowest_comparers.append((comparer, levens_dist))

    if lowest_comparers[:n]:
        return lowest_comparers[:n]

    else:
        return None

def closest_levenset(bad_list, good_list):
    count = 0
    for bad in bad_list:
        count+=1
        closest = closest_leven(bad, good_list)
        print(closest)
        yield bad, closest

def useful_levens(levenset, max_val=.2):
    for bad, levens in levenset:
        for good, leven_val in levens:
            if leven_val < .2:
                print(bad, good, leven_val)
                yield bad, good, leven_val
                continue #todo: generalize

if __name__ == '__main__':
    db = postgres_conn()
    good_streets = valid_streets(db)
    tkt_streets = ticket_streets(db)

    fh = open('/home/matt/git/chicago_tickets/data/corrections/levens.csv','w')
    writer = csv.writer(fh)

    unknowns = [ t for t in tkt_streets if t not in good_streets ]
    closest = closest_levenset(unknowns, good_streets)
    useful = useful_levens(closest)
    
    writer.writerows(useful)
