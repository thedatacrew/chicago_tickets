import sys, os, re
import cfg

from pprint import pprint
from usaddress import parse

def parse_address(addr_string):
    pre_parsed = {}
    parsed_list = parse(addr_string)

    for v, k in parsed_list:
        if k not in pre_parsed:
            pre_parsed[k] = []

        pre_parsed[k].append(v)

    parsed = {}
    for k,v in pre_parsed.items():
        parsed[k] = ' '.join(pre_parsed[k])

    try:
        addr_num = parsed['AddressNumber']
    except:
        addr_num = 0 
    try:
        post_type = parsed['StreetNamePostType']
    except:
        post_type = 0 
    try:
        post_dir = parsed['StreetNamePreDirectional']
    except:
        post_dir = None
    try:
        street_name = parsed['StreetName']
    except:

    keys = parsed.keys()
    if 'StreetNamePostType' not in keys:
        parsed['StreetNamePostType'] = ''
    if 'StreetNamePostType' not in  keys:
        parsed['StreetNamePostType'] = ''
    if 'StreetNamePreDirectional' not in  keys:
        parsed['StreetNamePreDirectional'] = ''
    if 'AddressNumber' not in keys:
        parsed['AddressNumber'] = -1

    return parsed, parsed_list

def clean_parsed(parsed):
    if 'PlaceName' in parsed:
        if parsed['PlaceName'] == "CHICAGO":
            parsed.pop('PlaceName')

    return parsed

def combine_streetnames(parsed_list):
    street_names = [ val for key,val in parsed_list if key == 'StreetName' ] 
    if len(street_names) > 1:
        street_names = ' '.join(street_names)
    else: 
        street_names = ''.join(street_names)

    return street_names


def correct_failures(parsed, test_failures):
    missing = [ i for i in test_failures if i[0] == 'missing' ]
    nodupes = [ i for i in test_failures if i[0] == 'nodupes' ]
    forbidden = [ i for i in test_failures if i[0] == 'forbidden' ]

    if forbidden:
        if 'PlaceName' in forbidden:
            if len(missing) == 1 and len(forbidden) == 1:
                parsed[missing[0]] = parsed.pop(forbidden[0])
                missing = []

    if nodupes:
        parsed = correct_nodupes(parsed, nodupes[0][1])

    if missing:
        parsed = correct_missing(parsed, missing[0][1])

    return parsed

def correct_missing(parsed, failvals):
    parsed = dict(parsed)
    keys =  parsed.keys()

    street_name = parsed['StreetName'] if 'StreetName' in parsed else None
    street_type = parsed['StreetNamePostType'] if 'StreetNamePostType' in parsed else None
    street_num = parsed['AddressNumber'] if 'AddressNumber' in parsed else None
    street_dir = parsed['StreetNamePreDirectional'] if 'StreetNamePreDirectional' in parsed else None

    if 'StreetName' in failvals:
        return parsed

    if 'StreetNamePostType' in failvals:
        if street_type:
            parsed.pop('StreetNamePreType')
            parsed['StreetNamePostType'] = street_type

    elif 'StreetNamePostType' in failvals:
        if len(streetname) == 1 and int(street_num) >= 9500:
            if 'StreetNamePreType' in keys:
                if street_type in ['AVENUE', 'AVE']:
                    parsed.pop('StreetNamePreType')
                    parsed['StreetName'] = street_type

    elif 'StreetNamePreDirectional' in failvals:
        street_name_len = len(street_name)
        if street_name_len == 1 and int(street_num) >= 9500:
            if 'StreetNamePostDirectional' in keys:
                if 'StreetNamePostType' in keys:
                    if street_type in ['AVENUE', 'AVE']:
                        parsed.pop('StreetNamePostDirectional')
                        parsed['StreetName'] = street_dir
                        parsed['StreetNamePreDirectional'] = 'S'

        if street_name_len == 1:
            if 'OccupancyIdentifier' in keys:
                occupancy_id = parsed.pop('OccupancyIdentifier')
                old_type = parsed.pop('StreetNamePostType')

                new_streetname = "%s %s" % (occupancy_id, old_type)
                new_dir = street_name

                parsed['StreetNamePreDirectional'] = new_dir
                parsed['StreetName'] = new_streetname

            else:
                if 'StreetNamePostType' in keys:
                    new_streetname = street_type
                    new_dir = street_name

                    parsed['StreetName'] = new_streetname
                    parsed['StreetNamePreDirectional'] = new_dir

    return parsed

def correct_nodupes(parsed, dupefails):
    good_dupes = ['StreetName']
    new_parsed = parsed

    for key, vals in dupefails.iteritems():
        if key in good_dupes and type(vals) == list:
            new_val = ' '.join(vals)
            new_parsed[key] = new_val

    return new_parsed

def correct_chiaddr(line):
    line = ','.join(line)
    newline = re.sub(r'([^,])-87\.',r'\1,-87.',line)
    newline = newline.split(',')

    return newline

def parse_ticket(ticket):
    return True

def parse_tickets(unparsed):
    return ( parse_ticket(ticket) for ticket in unparsed )
